#!/usr/bin/env python3
"""Validate the lightweight TDS documentation layer."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX = DOCS / "tds" / "DOCS-INDEX.yml"

REQUIRED_FRONTMATTER = (
    "tds_id",
    "tds_class",
    "status",
    "consumer",
    "source_of_truth",
    "evidence_level",
)

ALLOWED_CLASSES = {
    "index",
    "architecture",
    "adapter",
    "governance",
    "mesh",
    "eval",
    "evidence",
    "roadmap",
    "tds",
}

ALLOWED_STATUS = {"active", "proposed", "archived"}
ALLOWED_EVIDENCE = {"L0", "L1", "L2", "L3", "L4"}
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
DATE_MARKER = re.compile(r"\d{4}-\d{2}-\d{2}")
EVIDENCE_MARKERS = (
    "Run ID",
    "Git HEAD",
    "Dataset SHA",
    "Grader SHA",
    "Runner",
    "`gate_head`",
    "`run_head`",
    "`retention_head",
    "git_head",
    "retained run/hash",
    "commit",
    "SHA",
)


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    text = path.read_text(encoding="utf-8")
    failures: list[str] = []
    if not text.startswith("---\n"):
        return {}, [f"{path.relative_to(ROOT)} missing frontmatter"]

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, [f"{path.relative_to(ROOT)} has unterminated frontmatter"]

    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith("  ") or line.startswith("- "):
            continue
        if ":" not in line:
            failures.append(f"{path.relative_to(ROOT)} invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()

    for key in REQUIRED_FRONTMATTER:
        if not data.get(key):
            failures.append(f"{path.relative_to(ROOT)} missing frontmatter key: {key}")

    return data, failures


def parse_index() -> tuple[list[dict[str, str]], list[str]]:
    failures: list[str] = []
    if not INDEX.exists():
        return [], ["missing TDS index: docs/tds/DOCS-INDEX.yml"]

    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in INDEX.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- path:"):
            if current:
                entries.append(current)
            current = {"path": stripped.split(":", 1)[1].strip()}
            continue
        if current is not None and line.startswith("    ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip()

    if current:
        entries.append(current)

    if not entries:
        failures.append("TDS index has no documents")

    return entries, failures


def normalize_bool(value: str) -> str:
    return value.strip().lower()


def has_evidence_marker(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    relpath = str(path.relative_to(ROOT))
    return DATE_MARKER.search(relpath) is not None or DATE_MARKER.search(text) is not None or any(
        marker in text for marker in EVIDENCE_MARKERS
    )


def git_visible_doc_paths() -> set[Path]:
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
            "docs",
        ],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return {path.relative_to(ROOT) for path in DOCS.rglob("*.md")}
    return {
        Path(raw.decode("utf-8"))
        for raw in result.stdout.split(b"\0")
        if raw and Path(raw.decode("utf-8")).suffix == ".md"
    }


def validate_entry(entry: dict[str, str]) -> list[str]:
    failures: list[str] = []
    path = entry.get("path", "(missing path)")

    for key in ("path", "id", "class", "status", "consumer", "source_of_truth", "evidence_level"):
        if not entry.get(key):
            failures.append(f"{path} index entry missing key: {key}")

    if entry.get("class") and entry["class"] not in ALLOWED_CLASSES:
        failures.append(f"{path} has unknown TDS class: {entry['class']}")
    if entry.get("status") and entry["status"] not in ALLOWED_STATUS:
        failures.append(f"{path} has unknown status: {entry['status']}")
    if entry.get("evidence_level") and entry["evidence_level"] not in ALLOWED_EVIDENCE:
        failures.append(f"{path} has unknown evidence level: {entry['evidence_level']}")
    if entry.get("source_of_truth") and normalize_bool(entry["source_of_truth"]) not in {"true", "false"}:
        failures.append(f"{path} source_of_truth must be true or false")
    if entry.get("status") == "proposed" and normalize_bool(entry.get("source_of_truth", "")) == "true":
        failures.append(f"{path} proposed document cannot be source_of_truth")

    return failures


def main() -> int:
    failures: list[str] = []
    entries, index_failures = parse_index()
    failures.extend(index_failures)

    path_to_entry: dict[Path, dict[str, str]] = {}
    ids: dict[str, Path] = {}
    for entry in entries:
        failures.extend(validate_entry(entry))
        relpath = Path(entry.get("path", ""))
        if relpath in path_to_entry:
            failures.append(f"duplicate TDS index path: {relpath}")
        path_to_entry[relpath] = entry
        doc_id = entry.get("id")
        if doc_id:
            if doc_id in ids:
                failures.append(f"duplicate TDS id: {doc_id}")
            ids[doc_id] = relpath

    expected_paths = git_visible_doc_paths()
    expected_paths.add(Path("docs/tds/DOCS-INDEX.yml"))

    indexed_paths = set(path_to_entry)
    for path in sorted(expected_paths - indexed_paths):
        failures.append(f"document missing from TDS index: {path}")
    for path in sorted(indexed_paths - expected_paths):
        failures.append(f"TDS index path does not exist or is not governed: {path}")

    for relpath in sorted(expected_paths):
        path = ROOT / relpath
        if relpath.suffix != ".md":
            continue
        frontmatter, frontmatter_failures = parse_frontmatter(path)
        failures.extend(frontmatter_failures)
        entry = path_to_entry.get(relpath)
        if not entry:
            continue

        comparisons = (
            ("tds_id", "id"),
            ("tds_class", "class"),
            ("status", "status"),
            ("source_of_truth", "source_of_truth"),
            ("evidence_level", "evidence_level"),
        )
        for fm_key, index_key in comparisons:
            fm_value = frontmatter.get(fm_key)
            index_value = entry.get(index_key)
            if fm_key == "source_of_truth":
                fm_value = normalize_bool(fm_value or "")
                index_value = normalize_bool(index_value or "")
            if fm_value and index_value and fm_value != index_value:
                failures.append(
                    f"{relpath} frontmatter {fm_key}={fm_value} differs from index {index_key}={index_value}"
                )

        if frontmatter.get("consumer") != entry.get("consumer"):
            failures.append(f"{relpath} frontmatter consumer differs from index")

        tver = frontmatter.get("tver")
        if tver and not SEMVER.match(tver):
            failures.append(f"{relpath} frontmatter tver must be semver x.y.z")
        if (
            frontmatter.get("status") == "active"
            and normalize_bool(frontmatter.get("source_of_truth", "")) == "true"
            and not tver
        ):
            failures.append(f"{relpath} active source-of-truth document missing tver")
        if (
            frontmatter.get("tds_class") == "evidence"
            and frontmatter.get("status") == "active"
            and frontmatter.get("evidence_level") in {"L3", "L4"}
            and not has_evidence_marker(path)
        ):
            failures.append(f"{relpath} evidence report missing version, hash, run id, or Git marker")

    docs_index = ROOT / "docs/INDEX.md"
    if docs_index.exists():
        text = docs_index.read_text(encoding="utf-8")
        for required in ("tds/TDS-SPEC.md", "tds/DOCS-INDEX.yml"):
            if required not in text:
                failures.append(f"docs/INDEX.md missing TDS route: {required}")

    if failures:
        print("[tds] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[tds] PASS")
    print(f"documents={len(entries)}")
    print(f"index={INDEX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
