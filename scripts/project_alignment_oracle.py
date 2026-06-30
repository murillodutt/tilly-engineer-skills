#!/usr/bin/env python3
"""Validate TES project alignment mesh quality for installed targets.

The oracle enforces two layers:

1. Structural reconciliation: required mesh files, frontmatter, roadmap frame,
   evidence packet shape, Obsidian hygiene, and Glossary/Decisions presence.
2. Semantic reconciliation: a Semantic Residue Gate that loads a project-local
   contract under `docs/agents/contracts/SEMANTIC-RESIDUE.yml`, together with
   freshness reconciliation against the latest ADRs and retained evidence.

The semantic layer exists because a structural pass can still ship a false
green when active documentation asserts retired claims or implementation
vocabulary the project already moved past. TES owns the gate mechanism; the
target project owns the vocabulary.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.233"
PACKAGE_MODE = (ROOT / "scripts").exists()
AGENTS = Path("docs/agents")
EVIDENCE = AGENTS / "evidence"
DECISIONS = AGENTS / "DECISIONS"
RESIDUE_CONTRACT_PATHS = (
    AGENTS / "contracts/SEMANTIC-RESIDUE.yml",
    AGENTS / "contracts/semantic-residue.yml",
    AGENTS / "SEMANTIC-RESIDUE.yml",
)
RESIDUE_DEFAULT_SCOPE = (f"{AGENTS.as_posix()}/**",)
RESIDUE_DEFAULT_EXCLUDE = (
    f"{EVIDENCE.as_posix()}/**",
    f"{DECISIONS.as_posix()}/archive/**",
    f"{AGENTS.as_posix()}/contracts/**",
)
RESIDUE_SEVERITY_VALUES = {"fail", "needs_review", "warn"}
FRESHNESS_MESH_FILES = (
    "project_state",
    "project_roadmap",
    "execution_line",
    "project_context",
)
# Generic ADR/decision-record section headings and documentary scaffolding
# tokens that should not be reported as "new vocabulary introduced by the ADR".
# Keep this list small and limited to genuinely documentary words — the
# intent is to drop noise, not to silence real successor terms.
FRESHNESS_STOPWORDS = frozenset(
    {
        "accepted",
        "alternatives",
        "background",
        "consequences",
        "context",
        "decision",
        "decided",
        "deeper",
        "details",
        "evidence",
        "notes",
        "outcome",
        "overview",
        "proposed",
        "rationale",
        "references",
        "rejected",
        "section",
        "status",
        "summary",
        "superseded",
        "updated",
    }
)
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
DOCUMENTATION_AUTHORITY = AGENTS / "DOCUMENTATION-AUTHORITY.md"
CONTRACTS_DIR = AGENTS / "contracts"
FRONTMATTER_KEYS = ("tes_doc", "status", "updated", "confidence", "tags", "evidence")
ROADMAP_TERMS = ("Done", "Active", "Next", "Later", "Deferred", "Blocked", "Unknown")
ROADMAP_FRAME_TERMS = ("System X-Ray", "Convergence Line", "Current Claim", "Next Irreversible Step")
SYSTEM_XRAY_TERMS = (
    "Eraser Atlas View",
    ".tes/gps/project-overview.eraserdiagram",
    "Mermaid Fallback",
    "Git state",
    "Delivered behavior",
    "Validation mesh",
    "Release boundary",
    "classDef system",
)
CONVERGENCE_LINE_TERMS = (
    "Eraser Atlas View",
    ".tes/gps/project-gps.eraserdiagram",
    "Mermaid Fallback",
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
    "todo": re.compile(
        r"(?m)(?:^|\n)\s*(?:[-*]\s*)?(?:\[[ xX]\]\s*)?(?:TODO|todo)(?:\s*[:\-]\s*|\s*$)|"
        r"(?<![A-Za-z0-9_])TODO(?![A-Za-z0-9_])|"
        r"(?i:(?<![A-Za-z0-9_])todo\s+(?:fill\s+this\s+in|run\s+tests|fix\b|replace\b|add\b|write\b))"
    ),
    "lorem ipsum": re.compile(r"(?<![A-Za-z0-9_])lorem\s+ipsum(?![A-Za-z0-9_])", re.IGNORECASE),
    "fill this in": re.compile(r"(?<![A-Za-z0-9_])fill\s+this\s+in(?![A-Za-z0-9_])", re.IGNORECASE),
    "generic project": re.compile(r"(?<![A-Za-z0-9_])generic\s+project(?![A-Za-z0-9_])", re.IGNORECASE),
    "run tests": re.compile(r"(?<![A-Za-z0-9_])run\s+tests(?![A-Za-z0-9_/])", re.IGNORECASE),
    "to be determined": re.compile(r"(?<![A-Za-z0-9_])to\s+be\s+determined(?![A-Za-z0-9_])", re.IGNORECASE),
}
IMPLEMENTATION_DETAIL_PATTERNS = {
    "runtime endpoint": re.compile(
        r"(?<![A-Za-z0-9_])(?:api|http|rest|graphql)\s+endpoint(?![A-Za-z0-9_])|"
        r"(?<![A-Za-z0-9_])endpoint\s+implemented\b",
        re.IGNORECASE,
    ),
    "storage schema": re.compile(
        r"(?<![A-Za-z0-9_])(?:sql|database|db)\s+(?:table|schema|query|migration)(?![A-Za-z0-9_])",
        re.IGNORECASE,
    ),
    "runtime configuration": re.compile(
        r"(?<![A-Za-z0-9_])(?:environment variable|env var|config key)(?![A-Za-z0-9_])",
        re.IGNORECASE,
    ),
    "code construct": re.compile(
        r"(?<![A-Za-z0-9_])(?:function|method|class|handler|middleware|controller)(?![A-Za-z0-9_])",
        re.IGNORECASE,
    ),
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


def implementation_detail_failures(label: str, text: str) -> list[str]:
    failures: list[str] = []
    for lineno, line in enumerate(generic_search_text(text).splitlines(), start=1):
        for detail, pattern in IMPLEMENTATION_DETAIL_PATTERNS.items():
            if pattern.search(line):
                failures.append(
                    f"{label}:{lineno} contains implementation detail in language surface: {detail}"
                )
                break
    return failures


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


class ResidueContractError(ValueError):
    """Raised when a Semantic Residue contract file exists but is malformed.

    Carries the contract path so downstream code can emit a structured
    `residue.malformed_contract` finding with `severity`, `path`, and
    `reason` populated instead of relying on free-text failure lines.
    """

    def __init__(self, message: str, path: str | None = None) -> None:
        super().__init__(message)
        self.path = path


def load_residue_contract(target: Path) -> dict[str, Any] | None:
    """Load the project-local Semantic Residue contract.

    Returns the parsed mapping when a contract file is present and valid.
    Returns None when no contract is declared. Raises
    :class:`ResidueContractError` when a contract file is present but
    malformed so the oracle records a clear structured failure instead of
    silently skipping the gate.
    """
    for relpath in RESIDUE_CONTRACT_PATHS:
        path = target / relpath
        if not path.is_file():
            continue
        contract_path = relpath.as_posix()
        try:
            import yaml  # type: ignore[import-untyped]
        except Exception as exc:  # pragma: no cover - depends on env
            raise ResidueContractError(
                f"Semantic Residue contract {contract_path} requires PyYAML: {exc}",
                path=contract_path,
            ) from exc
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise ResidueContractError(
                f"Semantic Residue contract {contract_path} is not valid YAML: {exc}",
                path=contract_path,
            ) from exc
        if data is None:
            return {"version": 1, "entries": [], "_path": contract_path}
        if not isinstance(data, dict):
            raise ResidueContractError(
                f"Semantic Residue contract {contract_path} must be a mapping",
                path=contract_path,
            )
        data["_path"] = contract_path
        return data
    return None


def _normalize_scope(values: Any, fallback: tuple[str, ...]) -> tuple[str, ...]:
    if values is None:
        return tuple(fallback)
    if isinstance(values, str):
        return (values,)
    if isinstance(values, (list, tuple)):
        return tuple(str(item) for item in values if str(item).strip())
    return tuple(fallback)


def _glob_matches(relpath: str, patterns: tuple[str, ...]) -> bool:
    posix = relpath.replace("\\", "/")
    for pattern in patterns:
        if fnmatch.fnmatch(posix, pattern):
            return True
        # also support "docs/agents/**" matching "docs/agents/foo.md"
        if pattern.endswith("/**") and fnmatch.fnmatch(posix, pattern[:-3] + "/*"):
            return True
        if pattern.endswith("/**"):
            base = pattern[:-3]
            if posix == base or posix.startswith(base + "/"):
                return True
    return False


def _iter_scope_files(target: Path, scope: tuple[str, ...], exclude: tuple[str, ...]) -> list[Path]:
    seen: dict[str, Path] = {}
    for pattern in scope:
        # fnmatch globs over the whole tree; resolve via Path.rglob with a
        # filesystem-friendly base when the pattern is a tree pattern.
        if pattern.endswith("/**"):
            base = target / pattern[:-3]
            if base.is_dir():
                for path in base.rglob("*"):
                    if path.is_file():
                        seen[rel(path, target)] = path
            continue
        if pattern.endswith("/*"):
            base = target / pattern[:-2]
            if base.is_dir():
                for path in base.iterdir():
                    if path.is_file():
                        seen[rel(path, target)] = path
            continue
        for path in target.rglob(pattern.split("/")[-1]):
            if path.is_file() and _glob_matches(rel(path, target), (pattern,)):
                seen[rel(path, target)] = path
    return [path for relpath, path in sorted(seen.items()) if not _glob_matches(relpath, exclude)]


def _compile_term(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    return re.compile(rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])", re.IGNORECASE)


def _parse_date(value: Any) -> _dt.date | None:
    if value is None:
        return None
    if isinstance(value, _dt.date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return _dt.date.fromisoformat(text[:10])
    except ValueError:
        return None


def _match_lines(text: str, pattern: re.Pattern[str]) -> list[tuple[int, str]]:
    matches: list[tuple[int, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = pattern.search(line)
        if match:
            matches.append((lineno, match.group(0)))
    return matches


def semantic_residue_gate(
    target: Path,
    contract: dict[str, Any] | None,
    today: _dt.date,
) -> dict[str, Any]:
    """Apply the Semantic Residue Gate.

    Returns a structured result with `status`, `findings`, and `warnings`. The
    overall status escalates to `FAIL` on any `fail` severity match, to
    `NEEDS_REVIEW` on any `needs_review` match, and otherwise stays `PASS`.
    """
    if contract is None:
        return {
            "status": "PASS",
            "applied": False,
            "contract_path": None,
            "findings": [],
            "warnings": [
                "no Semantic Residue contract declared under docs/agents/contracts/SEMANTIC-RESIDUE.yml"
            ],
        }

    defaults = contract.get("defaults") or {}
    default_severity = str(defaults.get("severity", "needs_review")).lower()
    if default_severity not in RESIDUE_SEVERITY_VALUES:
        default_severity = "needs_review"
    default_scope = _normalize_scope(defaults.get("scope"), RESIDUE_DEFAULT_SCOPE)
    user_exclude = _normalize_scope(defaults.get("exclude"), RESIDUE_DEFAULT_EXCLUDE)
    # Always exclude the contract file itself so the residue gate cannot
    # self-trigger from declared vocabulary inside the contract YAML.
    contract_path = contract.get("_path")
    forced_exclude: tuple[str, ...] = ()
    if contract_path:
        forced_exclude = (contract_path,)
    default_exclude = tuple(dict.fromkeys(user_exclude + forced_exclude))

    entries_raw = contract.get("entries") or []
    if not isinstance(entries_raw, list):
        return {
            "status": "FAIL",
            "applied": True,
            "contract_path": contract.get("_path"),
            "findings": [
                {
                    "code": "residue.malformed_contract",
                    "severity": "fail",
                    "entry_id": None,
                    "path": contract.get("_path"),
                    "line": 0,
                    "match": None,
                    "reason": "entries must be a list",
                }
            ],
            "warnings": [],
        }

    findings: list[dict[str, Any]] = []
    warnings: list[str] = []
    status_rank = {"PASS": 0, "NEEDS_REVIEW": 1, "FAIL": 2}
    overall = "PASS"

    for index, raw in enumerate(entries_raw):
        if not isinstance(raw, dict):
            findings.append(
                {
                    "code": "residue.malformed_entry",
                    "severity": "fail",
                    "entry_id": None,
                    "path": contract.get("_path"),
                    "line": 0,
                    "match": None,
                    "reason": f"entries[{index}] must be a mapping",
                }
            )
            overall = "FAIL"
            continue
        entry_id = str(raw.get("id") or f"entry-{index}")
        term = raw.get("term")
        pattern_src = raw.get("pattern")
        if term and pattern_src:
            findings.append(
                {
                    "code": "residue.entry_conflict",
                    "severity": "fail",
                    "entry_id": entry_id,
                    "path": contract.get("_path"),
                    "line": 0,
                    "match": None,
                    "reason": "entry must declare exactly one of term or pattern",
                }
            )
            overall = "FAIL"
            continue
        if not term and not pattern_src:
            findings.append(
                {
                    "code": "residue.entry_missing_match",
                    "severity": "fail",
                    "entry_id": entry_id,
                    "path": contract.get("_path"),
                    "line": 0,
                    "match": None,
                    "reason": "entry must declare term or pattern",
                }
            )
            overall = "FAIL"
            continue

        try:
            pattern = _compile_term(str(term)) if term else re.compile(str(pattern_src))
        except re.error as exc:
            findings.append(
                {
                    "code": "residue.invalid_pattern",
                    "severity": "fail",
                    "entry_id": entry_id,
                    "path": contract.get("_path"),
                    "line": 0,
                    "match": None,
                    "reason": f"invalid regex pattern: {exc}",
                }
            )
            overall = "FAIL"
            continue

        severity = str(raw.get("severity", default_severity)).lower()
        if severity not in RESIDUE_SEVERITY_VALUES:
            severity = default_severity
        scope = _normalize_scope(raw.get("scope"), default_scope)
        exclude = _normalize_scope(raw.get("exclude"), default_exclude)
        allowed_paths = _normalize_scope(raw.get("allowed_paths"), tuple())
        reason = str(raw.get("reason", "")).strip()
        successor = str(raw.get("successor", "")).strip()
        expires = _parse_date(raw.get("expires_on"))
        if expires is not None and expires < today:
            warnings.append(
                f"semantic residue entry {entry_id} expired on {expires.isoformat()}; review or extend"
            )

        for path in _iter_scope_files(target, scope, exclude):
            relpath = rel(path, target)
            if allowed_paths and _glob_matches(relpath, allowed_paths):
                continue
            if not path.suffix.lower() in {".md", ".mdc", ".markdown", ".txt", ".yml", ".yaml"}:
                continue
            text = read_text(path)
            if not text:
                continue
            for lineno, snippet in _match_lines(text, pattern):
                finding = {
                    "code": "residue.match",
                    "severity": severity,
                    "entry_id": entry_id,
                    "path": relpath,
                    "line": lineno,
                    "match": snippet,
                    "reason": reason or "stale vocabulary present in active scope",
                }
                if successor:
                    finding["successor"] = successor
                findings.append(finding)
                if severity == "fail":
                    overall = "FAIL"
                elif severity == "needs_review" and status_rank[overall] < status_rank["NEEDS_REVIEW"]:
                    overall = "NEEDS_REVIEW"

    return {
        "status": overall,
        "applied": True,
        "contract_path": contract.get("_path"),
        "findings": findings,
        "warnings": warnings,
    }


def _newest_mtime(paths: list[Path]) -> float:
    return max((path.stat().st_mtime for path in paths if path.is_file()), default=0.0)


def freshness_reconciliation(target: Path) -> dict[str, Any]:
    """Compare current mesh against latest accepted ADRs and retained evidence.

    Heuristic only: returns warnings or `needs_review` items, never `FAIL`. The
    intent is to surface contradictions early so the agent re-reads the latest
    decision before claiming alignment.
    """
    notes: list[str] = []
    needs_review: list[dict[str, Any]] = []

    decisions_dir = target / DECISIONS
    adr_files = sorted(decisions_dir.glob("*.md")) if decisions_dir.is_dir() else []
    evidence_paths = evidence_files(target)

    if adr_files and evidence_paths:
        newest_adr = max(adr_files, key=lambda p: p.stat().st_mtime)
        newest_evidence = max(evidence_paths, key=lambda p: p.stat().st_mtime)
        if newest_adr.stat().st_mtime > newest_evidence.stat().st_mtime + 1.0:
            needs_review.append(
                {
                    "code": "freshness.adr_newer_than_evidence",
                    "severity": "needs_review",
                    "path": rel(newest_adr, target),
                    "reason": (
                        f"newest ADR {rel(newest_adr, target)} is newer than the latest "
                        f"alignment evidence packet {rel(newest_evidence, target)}; re-read "
                        "the ADR before claiming alignment"
                    ),
                }
            )

    if adr_files:
        newest_adr = max(adr_files, key=lambda p: p.stat().st_mtime)
        adr_text = read_text(newest_adr)
        mesh_text = ""
        for label in FRESHNESS_MESH_FILES:
            path = target / ALIGNMENT_FILES[label]
            mesh_text += "\n" + read_text(path)
        # heuristic: find tokens in CamelCase or kebab-case longer than 4 chars
        adr_tokens = {
            token
            for token in re.findall(r"\b[A-Za-z][A-Za-z0-9_-]{4,}\b", adr_text)
            if any(c.isupper() for c in token) or "-" in token
        }
        mesh_casefold = mesh_text.casefold()
        absent = sorted(
            token for token in adr_tokens
            if token.casefold() not in mesh_casefold
            and token.lower() not in FRESHNESS_STOPWORDS
        )
        if absent:
            notes.append(
                f"newest ADR {rel(newest_adr, target)} introduces tokens absent from "
                f"the active mesh: {', '.join(absent[:5])}"
            )

    # GAP-2: scaffold-only mesh detection. The initial /tes-init evidence packet
    # carries the literal "initial deterministic mesh" limit; a later /tes-align
    # refinement packet does not. Testing only the most-recent packet means the
    # signal clears the moment /tes-align rewrites the newest packet — no false
    # positive once the mesh has been semantically refined.
    mesh_scaffold_only = False
    if evidence_paths:
        newest_packet = max(evidence_paths, key=lambda p: p.stat().st_mtime)
        if "initial deterministic mesh" in read_text(newest_packet):
            mesh_scaffold_only = True

    return {
        "newest_adr": rel(adr_files[-1], target) if adr_files else None,
        "newest_evidence": rel(evidence_paths[-1], target) if evidence_paths else None,
        "mesh_scaffold_only": mesh_scaffold_only,
        "needs_review": needs_review,
        "notes": notes,
    }


def inventory_hygiene_gate(target: Path) -> dict[str, Any]:
    """Delegate to project-owned inventory runner when contract + script exist."""
    contract = target / "docs/agents/contracts/INVENTORY-HYGIENE.yml"
    script = target / "scripts" / "verify_documentation_inventory.py"
    packaged = target / ".tes/bin/verify_documentation_inventory.py"
    runner = script if script.is_file() else packaged
    if not contract.is_file():
        return {"applied": False, "status": "SKIP", "findings": []}
    if not runner.is_file():
        return {
            "applied": False,
            "status": "SKIP",
            "findings": [],
            "reason": (
                "INVENTORY-HYGIENE.yml present but no inventory runner "
                "(scripts/verify_documentation_inventory.py or "
                ".tes/bin/verify_documentation_inventory.py)"
            ),
        }
    proc = subprocess.run(
        [sys.executable, str(runner), "--target", str(target), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode not in (0, 2) and not proc.stdout.strip():
        return {
            "applied": True,
            "status": "FAIL",
            "findings": [
                {
                    "code": "inventory.runner_error",
                    "severity": "fail",
                    "path": runner.as_posix(),
                    "reason": proc.stderr.strip() or "inventory hygiene runner failed",
                }
            ],
        }
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {
            "applied": True,
            "status": "FAIL",
            "findings": [
                {
                    "code": "inventory.runner_error",
                    "severity": "fail",
                    "path": runner.as_posix(),
                    "reason": "inventory hygiene runner returned non-JSON output",
                }
            ],
        }
    if not isinstance(payload, dict):
        payload = {"applied": True, "status": "FAIL", "findings": []}
    payload.setdefault("applied", True)
    return payload


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
        if label == "glossary":
            failures.extend(implementation_detail_failures(relpath.as_posix(), text))
        if len(path_refs(text)) == 0 and label not in {"glossary"}:
            failures.append(f"{relpath.as_posix()} must cite at least one project path")

    # F10: per-surface required-surface signal. The scaffold decision must not
    # collapse the required mesh into a single umbrella flag — a consumer has to
    # be able to read which required surfaces are present vs absent. Absence is
    # already a hard failure above; this map exposes the per-surface presence so
    # a scaffold-tier pass cannot hide a missing required surface behind one
    # "scaffold-only" advisory.
    required_surfaces = {
        label: {"path": relpath.as_posix(), "present": docs[label]["exists"]}
        for label, relpath in ALIGNMENT_FILES.items()
    }
    required_surfaces_absent = sorted(
        info["path"] for info in required_surfaces.values() if not info["present"]
    )

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

    today = _dt.date.today()
    contract_error: ResidueContractError | None = None
    contract: dict[str, Any] | None = None
    try:
        contract = load_residue_contract(target)
    except ResidueContractError as exc:
        contract_error = exc
        failures.append(str(exc))

    residue = semantic_residue_gate(target, contract, today)
    if contract_error is not None:
        residue["status"] = "FAIL"
        residue["applied"] = True
        residue["contract_path"] = contract_error.path
        residue.setdefault("findings", []).append(
            {
                "code": "residue.malformed_contract",
                "severity": "fail",
                "entry_id": None,
                "path": contract_error.path,
                "line": 0,
                "match": None,
                "reason": str(contract_error),
            }
        )
    semantic_failures = [
        f"{item['path']}:{item['line']} stale residue [{item['entry_id']}] {item['match']!r}"
        for item in residue["findings"]
        if item["severity"] == "fail"
    ]
    semantic_needs_review = [
        f"{item['path']}:{item['line']} needs_review [{item['entry_id']}] {item['match']!r}"
        for item in residue["findings"]
        if item["severity"] == "needs_review"
    ]
    semantic_warn = [
        f"{item['path']}:{item['line']} warn [{item['entry_id']}] {item['match']!r}"
        for item in residue["findings"]
        if item["severity"] == "warn"
    ]
    failures.extend(semantic_failures)
    warnings.extend(residue.get("warnings", []))
    warnings.extend(semantic_warn)

    freshness = freshness_reconciliation(target)
    warnings.extend(freshness.get("notes", []))

    if not freshness.get("mesh_scaffold_only", False):
        if not read_text(target / DOCUMENTATION_AUTHORITY).strip():
            failures.append("missing alignment surface: docs/agents/DOCUMENTATION-AUTHORITY.md")
        contract_files = (
            sorted(path for path in (target / CONTRACTS_DIR).rglob("*") if path.is_file())
            if (target / CONTRACTS_DIR).is_dir()
            else []
        )
        if not contract_files:
            failures.append("missing alignment surface: docs/agents/contracts/** (at least one contract file required)")

    inventory = inventory_hygiene_gate(target)
    inventory_failures = [
        f"inventory hygiene: {item.get('reason', item.get('code', 'unknown'))}"
        for item in inventory.get("findings", [])
        if item.get("severity") == "fail"
    ]
    inventory_needs_review = [
        f"inventory hygiene: {item.get('reason', item.get('code', 'unknown'))}"
        for item in inventory.get("findings", [])
        if item.get("severity") == "needs_review"
    ]
    failures.extend(inventory_failures)

    # CEILING: absence of proof never becomes the same green as proof, and
    # scaffold is its own tier. A clean structural + semantic pass on a mesh
    # that has NOT yet been refined via /tes-align (the initial deterministic
    # scaffold) reads `PASS_SCAFFOLD`, distinct from the aligned `PASS_ALIGNED`.
    # FAIL and NEEDS_REVIEW still take precedence — scaffold tier only applies
    # to a mesh that would otherwise read fully green. Both PASS tiers exit 0
    # (scaffold is not a failure; the protected baseline keeps a genuinely
    # scaffold-only project installing green).
    if failures:
        status = "FAIL"
    elif semantic_needs_review or freshness.get("needs_review") or inventory_needs_review:
        status = "NEEDS_REVIEW"
    elif freshness.get("mesh_scaffold_only") is True:
        status = "PASS_SCAFFOLD"
    else:
        status = "PASS_ALIGNED"

    return {
        "version": VERSION,
        "status": status,
        "target": str(target),
        "docs": docs,
        "required_surfaces": required_surfaces,
        "required_surfaces_absent": required_surfaces_absent,
        "evidence_packets": [rel(path, target) for path in retained],
        "failures": failures,
        "warnings": warnings,
        "semantic_residue": residue,
        "freshness": freshness,
        "inventory_hygiene": inventory,
        "needs_review": semantic_needs_review
        + inventory_needs_review
        + [item["reason"] for item in freshness.get("needs_review", [])],
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
    return """### Eraser Atlas View

- Primary visual: `.tes/gps/project-overview.eraserdiagram`

### Mermaid Fallback

```mermaid
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
    return """### Eraser Atlas View

- Primary visual: `.tes/gps/project-gps.eraserdiagram`

### Mermaid Fallback

```mermaid
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
        DOCUMENTATION_AUTHORITY,
        fm("documentation-authority")
        + "# Documentation Authority\n\nTier 1: `docs/project/super-spec.md`. "
        + "Related: [[PROJECT-STATE]], [[PROJECT-ROADMAP]], [[QUALITY-GATES]].\n",
    )
    write(
        CONTRACTS_DIR / "OPERATING-MESH.yml",
        "version: 1\nscope:\n  - docs/agents/**\n",
    )
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
        + "  tes_version: 0.3.233\n"
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


def write_residue_contract(
    target: Path,
    severity: str = "fail",
    term_override: str | None = None,
) -> None:
    """Write a minimal Semantic Residue contract for self-test fixtures.

    The contract uses synthetic vocabulary (`canary-retired-term`) so the
    self-test never depends on real project-specific language.
    """
    term = term_override or "canary-retired-term"
    contract_path = target / RESIDUE_CONTRACT_PATHS[0]
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "version: 1\n"
        "defaults:\n"
        "  severity: needs_review\n"
        "  scope:\n"
        "    - docs/agents/**\n"
        "  exclude:\n"
        "    - docs/agents/evidence/**\n"
        "    - docs/agents/contracts/**\n"
        "entries:\n"
        f"  - id: canary-retired\n"
        f"    term: \"{term}\"\n"
        f"    severity: {severity}\n"
        "    reason: \"Replaced by current-runtime-term per ADR-0001.\"\n"
        "    successor: \"current-runtime-term\"\n"
        "    allowed_paths:\n"
        "      - docs/agents/evidence/**\n"
    )
    contract_path.write_text(body, encoding="utf-8")


def self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tes-align-good-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        result = analyze(target)
        # The good fixture ships a refined evidence packet (limits: sparse
        # fixture, not the scaffold literal), so it must read PASS_ALIGNED.
        if result["status"] != "PASS_ALIGNED":
            failures.extend([f"good fixture must pass aligned: {item}" for item in result["failures"]])
        if result["status"] != "PASS_ALIGNED":
            failures.append(f"good fixture must read PASS_ALIGNED, got {result['status']}")

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
        if result["status"] != "PASS_ALIGNED":
            failures.extend(
                [f"literal placeholder fixture must pass: {item}" for item in result["failures"]]
            )

    with tempfile.TemporaryDirectory(prefix="tes-align-ptbr-prose-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        path = target / ALIGNMENT_FILES["glossary"]
        path.write_text(
            read_text(path)
            + "\n## Connector Framework\n\n"
            + "Em portugues, todo conector precisa satisfazer o contrato ativo.\n",
            encoding="utf-8",
        )
        result = analyze(target)
        if result["status"] != "PASS_ALIGNED":
            failures.extend([f"pt-br prose fixture must pass: {item}" for item in result["failures"]])

    with tempfile.TemporaryDirectory(prefix="tes-align-glossary-implementation-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        path = target / ALIGNMENT_FILES["glossary"]
        path.write_text(
            read_text(path)
            + "\n| Webhook | HTTP endpoint implemented by `src/webhook.ts`, backed by a SQL table and environment variable. |\n",
            encoding="utf-8",
        )
        result = analyze(target)
        if result["status"] != "FAIL" or not any("implementation detail" in item for item in result["failures"]):
            failures.append("glossary fixture must fail implementation-heavy language")

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

    # Semantic residue: stale current claim in active doc must fail or
    # mark needs_review under the project-local contract.
    with tempfile.TemporaryDirectory(prefix="tes-align-residue-fail-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        write_residue_contract(target, severity="fail")
        state_path = target / ALIGNMENT_FILES["project_state"]
        state_path.write_text(
            read_text(state_path)
            + "\n## Active Architecture\n\nThe canary-retired-term backend is the current runtime.\n",
            encoding="utf-8",
        )
        result = analyze(target)
        if result["status"] != "FAIL" or not any(
            "canary-retired-term" in item or "stale residue" in item for item in result["failures"]
        ):
            failures.append("residue gate must fail when active doc asserts a retired term")
        residue = result.get("semantic_residue") or {}
        if not residue.get("applied"):
            failures.append("residue gate must mark applied when contract is present")

    # Semantic residue: historical evidence retains the retired term under
    # explicit allowlist, oracle should pass.
    with tempfile.TemporaryDirectory(prefix="tes-align-residue-allow-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        write_residue_contract(target, severity="fail")
        evidence_path = target / EVIDENCE / "20260101T000000Z-historical-alignment.md"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(
            "# Historical Alignment\n\n"
            "Past current-state language used canary-retired-term as the runtime claim.\n",
            encoding="utf-8",
        )
        result = analyze(target)
        if result["status"] != "PASS_ALIGNED":
            failures.extend(
                [
                    f"residue allowlist fixture must pass: {item}"
                    for item in result.get("failures", [])
                    if "canary-retired-term" in item or "stale residue" in item
                ]
            )

    # Semantic residue: word boundary must not flag unrelated longer words.
    # A short retired literal must not match a longer unrelated word that
    # contains it as a substring. This is the regression for the naive
    # substring class that produced the original false fail.
    with tempfile.TemporaryDirectory(prefix="tes-align-residue-boundary-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        write_residue_contract(target, severity="fail", term_override="port")
        state_path = target / ALIGNMENT_FILES["project_state"]
        state_path.write_text(
            read_text(state_path)
            + "\nThis report covers nothing related to the retired term.\n",
            encoding="utf-8",
        )
        result = analyze(target)
        if result["status"] != "PASS_ALIGNED":
            failures.append(
                "residue boundary fixture must pass; short literal must not match a longer unrelated word"
            )

    # Semantic residue: malformed entry must surface a clear failure code.
    with tempfile.TemporaryDirectory(prefix="tes-align-residue-malformed-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        contract_path = target / RESIDUE_CONTRACT_PATHS[0]
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(
            "version: 1\nentries:\n  - id: bad\n    term: stale\n    pattern: also-stale\n",
            encoding="utf-8",
        )
        result = analyze(target)
        if result["status"] != "FAIL" or not any(
            "exactly one of term or pattern" in str(item)
            for item in (result.get("semantic_residue") or {}).get("findings", [])
        ):
            failures.append(
                "residue malformed entry fixture must fail with explicit code"
            )

    # Semantic residue: malformed contract YAML (top-level) must surface a
    # structured finding in semantic_residue.findings, not only as a
    # free-text failure line. This regression was reported by the canary
    # review on 2026-05-25.
    with tempfile.TemporaryDirectory(prefix="tes-align-residue-broken-yaml-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        contract_path = target / RESIDUE_CONTRACT_PATHS[0]
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(
            "version: 1\nentries: [this is: not valid yaml at all\n",
            encoding="utf-8",
        )
        result = analyze(target)
        residue = result.get("semantic_residue") or {}
        malformed_findings = [
            item
            for item in residue.get("findings", [])
            if item.get("code") == "residue.malformed_contract"
        ]
        if (
            result["status"] != "FAIL"
            or residue.get("status") != "FAIL"
            or not residue.get("applied")
            or residue.get("contract_path") != RESIDUE_CONTRACT_PATHS[0].as_posix()
            or not malformed_findings
            or malformed_findings[0].get("severity") != "fail"
            or malformed_findings[0].get("path") != RESIDUE_CONTRACT_PATHS[0].as_posix()
            or not malformed_findings[0].get("reason")
        ):
            failures.append(
                "broken YAML contract fixture must emit a structured "
                "residue.malformed_contract finding with severity, path, "
                "and reason populated"
            )

    # Freshness reconciliation: an ADR that only uses generic documentary
    # headings (Consequences, Decision, Status, Context, Rationale, ...)
    # must not generate a freshness note. Without the stopword filter the
    # canary review reported false positives on Consequences and Deeper.
    with tempfile.TemporaryDirectory(prefix="tes-align-freshness-stopwords-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        adr_path = target / DECISIONS / "002-doc-only-adr.md"
        adr_path.parent.mkdir(parents=True, exist_ok=True)
        adr_path.write_text(
            "# ADR 002\n\n## Status\nAccepted\n\n## Context\nBackground notes.\n\n"
            "## Decision\nNo change.\n\n## Consequences\nNone material.\n\n"
            "## Rationale\nDeeper explanation here.\n\n## Alternatives\nNone.\n",
            encoding="utf-8",
        )
        result = analyze(target)
        freshness_notes = (result.get("freshness") or {}).get("notes") or []
        offenders = [
            note
            for note in freshness_notes
            if any(
                word in note
                for word in ("Consequences", "Deeper", "Rationale", "Alternatives", "Background")
            )
        ]
        if offenders:
            failures.append(
                "freshness stopword fixture must not flag generic ADR headings: "
                + "; ".join(offenders)
            )

    # GAP-2: scaffold-only mesh detection keys off the most-recent evidence
    # packet. A scaffold packet carrying the literal limit flags scaffold_only;
    # a newer /tes-align refinement packet clears it (no false positive).
    with tempfile.TemporaryDirectory(prefix="tes-align-scaffold-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        evidence_dir = target / EVIDENCE
        evidence_dir.mkdir(parents=True, exist_ok=True)
        # Make the scaffold packet unambiguously the newest one (the fixture
        # already wrote an evidence packet with a near-current mtime).
        scaffold_packet = evidence_dir / "20260101T000000Z-project-alignment.md"
        scaffold_packet.write_text(
            "# Alignment Evidence\n\nlimits: initial deterministic mesh; run /tes-align "
            "for deeper semantic refinement\n",
            encoding="utf-8",
        )
        os.utime(scaffold_packet, (2_000_000_000, 2_000_000_000))
        fresh = freshness_reconciliation(target)
        if fresh.get("mesh_scaffold_only") is not True:
            failures.append("scaffold-only mesh must be detected from the initial evidence packet")
        # A later /tes-align refinement packet (no scaffold limit) clears the flag.
        refined_packet = evidence_dir / "20260601T000000Z-project-alignment.md"
        refined_packet.write_text(
            "# Alignment Evidence\n\nlimits: semantic refinement applied; mesh reflects domain\n",
            encoding="utf-8",
        )
        os.utime(refined_packet, (2_100_000_000, 2_100_000_000))
        refined = freshness_reconciliation(target)
        if refined.get("mesh_scaffold_only") is not False:
            failures.append("scaffold-only flag must clear once a refinement packet is newest")

    # F13 CEILING: scaffold is its own tier. A clean structural + semantic pass
    # on a mesh that is still the initial deterministic scaffold must read
    # PASS_SCAFFOLD, NOT the same green as an aligned mesh (PASS_ALIGNED). This
    # is RED-capable: before the tier split both states collapsed to "PASS",
    # so a scaffold mesh read identically to a /tes-align-refined mesh.
    with tempfile.TemporaryDirectory(prefix="tes-align-tier-scaffold-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        evidence_dir = target / EVIDENCE
        evidence_dir.mkdir(parents=True, exist_ok=True)
        # Replace the refined evidence packet with the initial scaffold packet so
        # the newest packet carries the scaffold literal. Everything else in the
        # good fixture stays valid, so the only change is the tier.
        scaffold_packet = evidence_dir / "20260601T000000Z-project-alignment.md"
        scaffold_packet.write_text(
            "# Project Alignment Evidence\n\n"
            + "```yaml\nalignment_evidence:\n"
            + "  target: fixture\n"
            + "  anchors_read:\n"
            + "    - README.md\n"
            + "    - package.json\n"
            + "    - src/app.ts\n"
            + "  quality_gates_discovered:\n"
            + "    - npm test\n"
            + "  limits: initial deterministic mesh; run /tes-align for refinement\n```\n",
            encoding="utf-8",
        )
        os.utime(scaffold_packet, (2_100_000_000, 2_100_000_000))
        result = analyze(target)
        if result["status"] != "PASS_SCAFFOLD":
            failures.append(
                "scaffold-only mesh must read PASS_SCAFFOLD, not "
                f"{result['status']} (scaffold is its own tier, not aligned green)"
            )
        if result["status"] == "PASS_ALIGNED":
            failures.append(
                "scaffold-only mesh must NOT read PASS_ALIGNED — absence of "
                "/tes-align refinement cannot read as proof of alignment"
            )
        # F10: the per-surface required-surface signal must be present and report
        # every required surface, so a scaffold-tier pass cannot hide a missing
        # required surface behind one umbrella advisory.
        required = result.get("required_surfaces") or {}
        if set(required) != set(ALIGNMENT_FILES):
            failures.append(
                "scaffold result must expose a per-surface required_surfaces signal "
                "covering every required alignment surface"
            )
        if not all(info.get("present") for info in required.values()):
            failures.append(
                "scaffold fixture has all required surfaces present; required_surfaces "
                "must report present=True for each"
            )
        if result.get("required_surfaces_absent"):
            failures.append(
                "scaffold fixture with all surfaces present must report no absent surfaces"
            )

    # F10 RED-capable: a missing required surface must be named in the per-surface
    # absent signal (not hidden behind the scaffold advisory) and must FAIL.
    with tempfile.TemporaryDirectory(prefix="tes-align-tier-absent-") as tempdir:
        target = Path(tempdir)
        write_good_fixture(target)
        missing = target / ALIGNMENT_FILES["execution_line"]
        missing.unlink()
        result = analyze(target)
        if result["status"] != "FAIL":
            failures.append("missing required surface must FAIL, never a scaffold-tier pass")
        absent = result.get("required_surfaces_absent") or []
        if ALIGNMENT_FILES["execution_line"].as_posix() not in absent:
            failures.append(
                "per-surface absent signal must name the missing required surface "
                f"{ALIGNMENT_FILES['execution_line'].as_posix()}"
            )

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
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit only the machine-readable JSON body; suppress the trailing tag line.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on NEEDS_REVIEW as well as FAIL.",
    )
    args = parser.parse_args()

    result = self_test() if args.self_test else analyze(args.target)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json:
        print("[project-alignment] " + result["status"])
    if result["status"] == "FAIL":
        return 1
    if result["status"] == "NEEDS_REVIEW" and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
