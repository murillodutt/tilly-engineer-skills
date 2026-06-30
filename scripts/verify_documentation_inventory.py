#!/usr/bin/env python3
"""Verify Tier 3 PROJECT-CONTEXT inventory hygiene for documentation authority.

Enforces docs/agents/contracts/INVENTORY-HYGIENE.yml when present.
Invoked by project quality gates and project_alignment_oracle.py.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

CONTRACT_PATHS = (
    Path("docs/agents/contracts/INVENTORY-HYGIENE.yml"),
    Path("docs/agents/contracts/inventory-hygiene.yml"),
)

def fixture_contract_path() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (
        here / "fixtures" / "INVENTORY-HYGIENE.minimal.yml",
        here.parent / "fixtures" / "INVENTORY-HYGIENE.minimal.yml",
    ):
        if candidate.is_file():
            return candidate
    return here / "fixtures" / "INVENTORY-HYGIENE.minimal.yml"


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def load_contract(target: Path) -> dict[str, Any] | None:
    if yaml is None:
        return None
    for rel in CONTRACT_PATHS:
        path = target / rel
        if path.is_file():
            data = yaml.safe_load(read_text(path))
            if isinstance(data, dict):
                return data
    return None


def git_head(target: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def git_parent_head(target: Path) -> str | None:
    """Return HEAD~1 when the target is a Git worktree with history."""
    try:
        result = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "HEAD~1"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def git_object_exists(target: Path, ref: str) -> bool:
    try:
        subprocess.run(
            ["git", "-C", str(target), "rev-parse", "--verify", f"{ref}^{{commit}}"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def git_is_ancestor(target: Path, ancestor: str, descendant: str) -> bool:
    try:
        subprocess.run(
            ["git", "-C", str(target), "merge-base", "--is-ancestor", ancestor, descendant],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def git_head_row_matches(
    mesh_head: str,
    repository_head: str | None,
    target: Path | None = None,
    parent_head: str | None = None,
) -> bool:
    """Return True when the Identity Git HEAD row matches the repository state.

    Accept exact HEAD, short-hash prefix, immediate parent after a mesh-only
    commit, or any documented commit that is a Git ancestor of current HEAD.
    """
    if not repository_head:
        return False
    if mesh_head == repository_head:
        return True
    if repository_head.startswith(mesh_head):
        return True
    if parent_head and (mesh_head == parent_head or parent_head.startswith(mesh_head)):
        return True
    if target and git_object_exists(target, mesh_head) and git_is_ancestor(target, mesh_head, "HEAD"):
        return True
    return False


def extract_section(text: str, heading: str) -> str:
    pattern = re.compile(
        rf"^{re.escape(heading)}\s*$(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1) if match else ""


def frontmatter_value(text: str, key: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    for line in block.splitlines():
        if line.strip().startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def analyze(target: Path) -> dict[str, Any]:
    target = target.resolve()
    contract = load_contract(target)
    findings: list[dict[str, Any]] = []

    if contract is None:
        return {
            "status": "SKIP",
            "applied": False,
            "reason": "INVENTORY-HYGIENE.yml not found or PyYAML unavailable",
            "findings": [],
        }

    for req in contract.get("requires") or []:
        if not isinstance(req, dict):
            continue
        rel = req.get("path")
        if not rel:
            continue
        path = target / str(rel)
        if not path.is_file():
            findings.append(
                {
                    "code": "inventory.missing_required",
                    "severity": req.get("severity", "fail"),
                    "path": str(rel),
                    "reason": f"required file missing: {rel}",
                }
            )

    pc = contract.get("project_context") or {}
    pc_path = target / str(pc.get("path", "docs/agents/PROJECT-CONTEXT.md"))
    pc_text = read_text(pc_path)
    if not pc_text:
        findings.append(
            {
                "code": "inventory.missing_project_context",
                "severity": "fail",
                "path": pc.get("path", "docs/agents/PROJECT-CONTEXT.md"),
                "reason": "PROJECT-CONTEXT.md missing",
            }
        )
    else:
        expected_tier = pc.get("frontmatter_tier")
        if expected_tier:
            actual_tier = frontmatter_value(pc_text, "tier")
            if actual_tier != expected_tier:
                findings.append(
                    {
                        "code": "inventory.tier_frontmatter",
                        "severity": "fail",
                        "path": pc_path.relative_to(target).as_posix(),
                        "reason": (
                            f"frontmatter tier must be {expected_tier!r}, "
                            f"got {actual_tier!r}"
                        ),
                    }
                )

        if pc.get("git_head_must_match"):
            head = git_head(target)
            parent = git_parent_head(target)
            if head:
                match = re.search(r"Git HEAD\s*\|\s*`([0-9a-f]{7,40})`", pc_text)
                if not match:
                    findings.append(
                        {
                            "code": "inventory.stale_git_head",
                            "severity": "needs_review",
                            "path": pc_path.relative_to(target).as_posix(),
                            "reason": "Identity table missing Git HEAD row",
                        }
                    )
                elif not git_head_row_matches(match.group(1), head, target, parent):
                    findings.append(
                        {
                            "code": "inventory.stale_git_head",
                            "severity": "needs_review",
                            "path": pc_path.relative_to(target).as_posix(),
                            "reason": (
                                f"Git HEAD {match.group(1)} does not match "
                                f"repository {head}"
                            ),
                        }
                    )

        section_heading = str(pc.get("deep_reads_section", "## Recommended Deep Reads"))
        deep_reads = extract_section(pc_text, section_heading)
        if deep_reads:
            bullet_lines = [
                line.strip()
                for line in deep_reads.splitlines()
                if line.strip().startswith("- ")
            ]
            bullets_text = "\n".join(bullet_lines)
            for forbidden in pc.get("forbidden_deep_read_paths") or []:
                token = str(forbidden)
                if token in bullets_text:
                    findings.append(
                        {
                            "code": "inventory.tier4_deep_read",
                            "severity": "fail",
                            "path": pc_path.relative_to(target).as_posix(),
                            "match": token,
                            "reason": (
                                f"Tier 4 or retired path {token!r} listed as a deep-read "
                                f"bullet under {section_heading}"
                            ),
                        }
                    )
            for pointer in pc.get("required_deep_read_pointers") or []:
                if str(pointer) not in deep_reads and f"[[{pointer}]]" not in deep_reads:
                    findings.append(
                        {
                            "code": "inventory.missing_deep_read_pointer",
                            "severity": "fail",
                            "path": pc_path.relative_to(target).as_posix(),
                            "match": str(pointer),
                            "reason": (
                                f"{section_heading} must point agents to {pointer}"
                            ),
                        }
                    )

    fail = [f for f in findings if f.get("severity") == "fail"]
    review = [f for f in findings if f.get("severity") == "needs_review"]
    if fail:
        status = "FAIL"
    elif review:
        status = "NEEDS_REVIEW"
    else:
        status = "PASS"

    return {
        "status": status,
        "applied": True,
        "contract_path": CONTRACT_PATHS[0].as_posix(),
        "findings": findings,
    }


def self_test() -> dict[str, Any]:
    import tempfile

    failures: list[str] = []
    fixture_path = fixture_contract_path()
    if not fixture_path.is_file():
        return {
            "status": "FAIL",
            "failures": [f"missing fixture contract: {fixture_path}"],
        }
    fixture_yaml = read_text(fixture_path)

    with tempfile.TemporaryDirectory(prefix="inv-hygiene-good-") as tempdir:
        target = Path(tempdir)
        contract_dir = target / "docs/agents/contracts"
        contract_dir.mkdir(parents=True)
        (contract_dir / "INVENTORY-HYGIENE.yml").write_text(fixture_yaml, encoding="utf-8")
        (target / "docs/agents/DOCUMENTATION-AUTHORITY.md").write_text("# ok\n", encoding="utf-8")
        (target / "docs/agents/PROJECT-CONTEXT.md").write_text(
            "---\ntier: 3-inventory\n---\n\n## Identity\n\n| Git HEAD | `abc` |\n\n"
            "## Recommended Deep Reads\n\n- [[DOCUMENTATION-AUTHORITY]]\n- [[EXECUTION-LINE]]\n",
            encoding="utf-8",
        )
        result = analyze(target)
        if result["status"] != "PASS":
            failures.append(f"good fixture expected PASS got {result['status']}")

    with tempfile.TemporaryDirectory(prefix="inv-hygiene-bad-") as tempdir:
        target = Path(tempdir)
        contract_dir = target / "docs/agents/contracts"
        contract_dir.mkdir(parents=True)
        (contract_dir / "INVENTORY-HYGIENE.yml").write_text(fixture_yaml, encoding="utf-8")
        (target / "docs/agents/DOCUMENTATION-AUTHORITY.md").write_text("# ok\n", encoding="utf-8")
        (target / "docs/agents/PROJECT-CONTEXT.md").write_text(
            "---\ntier: 3-inventory\n---\n\n## Recommended Deep Reads\n\n"
            "- docs/archive-retired/README.md\n",
            encoding="utf-8",
        )
        result = analyze(target)
        if result["status"] != "FAIL":
            failures.append("forbidden deep read fixture must FAIL")

    with tempfile.TemporaryDirectory(prefix="inv-hygiene-git-head-parent-") as tempdir:
        target = Path(tempdir)
        contract_dir = target / "docs/agents/contracts"
        contract_dir.mkdir(parents=True)
        (contract_dir / "INVENTORY-HYGIENE.yml").write_text(fixture_yaml, encoding="utf-8")
        (target / "docs/agents/DOCUMENTATION-AUTHORITY.md").write_text("# ok\n", encoding="utf-8")
        subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
        subprocess.run(["git", "-C", str(target), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(target), "config", "user.name", "test"], check=True)
        (target / "README.md").write_text("# fixture\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(target), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(target), "commit", "-m", "first"], check=True)
        parent = git_head(target)
        (target / "docs/agents/PROJECT-CONTEXT.md").write_text(
            f"---\ntier: 3-inventory\n---\n\n## Identity\n\n| Git HEAD | `{parent}` |\n\n"
            "## Recommended Deep Reads\n\n- [[DOCUMENTATION-AUTHORITY]]\n- [[EXECUTION-LINE]]\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "-C", str(target), "add", "docs/agents/PROJECT-CONTEXT.md"], check=True)
        subprocess.run(["git", "-C", str(target), "commit", "-m", "mesh head sync"], check=True)
        result = analyze(target)
        if result["status"] != "PASS":
            failures.append(
                "mesh-only Git HEAD commit must PASS when Identity row records parent HEAD"
            )

    with tempfile.TemporaryDirectory(prefix="inv-hygiene-git-head-ancestor-") as tempdir:
        target = Path(tempdir)
        contract_dir = target / "docs/agents/contracts"
        contract_dir.mkdir(parents=True)
        (contract_dir / "INVENTORY-HYGIENE.yml").write_text(fixture_yaml, encoding="utf-8")
        (target / "docs/agents/DOCUMENTATION-AUTHORITY.md").write_text("# ok\n", encoding="utf-8")
        subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
        subprocess.run(["git", "-C", str(target), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(target), "config", "user.name", "test"], check=True)
        (target / "README.md").write_text("# fixture\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(target), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(target), "commit", "-m", "first"], check=True)
        documented = git_head(target)
        (target / "docs/agents/PROJECT-CONTEXT.md").write_text(
            f"---\ntier: 3-inventory\n---\n\n## Identity\n\n| Git HEAD | `{documented}` |\n\n"
            "## Recommended Deep Reads\n\n- [[DOCUMENTATION-AUTHORITY]]\n- [[EXECUTION-LINE]]\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "-C", str(target), "add", "docs/agents/PROJECT-CONTEXT.md"], check=True)
        subprocess.run(["git", "-C", str(target), "commit", "-m", "mesh head sync"], check=True)
        (target / "NOTES.md").write_text("follow-up\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(target), "add", "NOTES.md"], check=True)
        subprocess.run(["git", "-C", str(target), "commit", "-m", "follow-up without mesh refresh"], check=True)
        result = analyze(target)
        if result["status"] != "PASS":
            failures.append(
                "Identity Git HEAD at an ancestor of HEAD must PASS without immediate mesh refresh"
            )

    return {"status": "PASS" if not failures else "FAIL", "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = self_test() if args.self_test else analyze(args.target)
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json:
        print("[documentation-inventory] " + result["status"])
    if result["status"] == "FAIL":
        return 1
    if result["status"] == "NEEDS_REVIEW":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
