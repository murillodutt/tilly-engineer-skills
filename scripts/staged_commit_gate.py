#!/usr/bin/env python3
"""Intelligent staged-file commit gate — default `npm run commit:check`.

Routes validation to the smallest gates implied by staged paths instead of
running the full repository closure on every commit. Use `npm run commit:closure`
only when explicitly requested.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.223"

TEXT_SCAN_SUFFIXES = {
    ".md",
    ".mdc",
    ".py",
    ".json",
    ".jsonl",
    ".ndjson",
    ".yml",
    ".yaml",
    ".html",
    ".txt",
    ".js",
    ".ts",
    ".mjs",
}

LOCAL_DEVELOPMENT_SKILL_PARITY = (
    "tes-engineering-discipline",
    "tes-high-agency-pattern",
    "tes-landing-authoring",
    "tes-manual-authoring",
    "tes-mine",
    "tes-predictive-operations",
    "tes-prospect",
    "tes-sync",
    "tes-goal-maestro",
    "vozza",
)


@dataclass(frozen=True)
class Gate:
    gate_id: str
    command: list[str]
    matcher: Callable[[list[Path]], bool] | None = None
    file_filter: Callable[[Path], bool] | None = None


def git_staged_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [Path(raw.decode("utf-8")) for raw in result.stdout.split(b"\0") if raw]


def any_match(staged: list[Path], patterns: tuple[str, ...]) -> bool:
    for path in staged:
        rel = path.as_posix()
        if any(fnmatch.fnmatch(rel, pattern) for pattern in patterns):
            return True
    return False


def suffix_match(staged: list[Path], suffixes: set[str]) -> bool:
    return any(path.suffix.lower() in suffixes for path in staged)


def touched_dev_skills(staged: list[Path]) -> set[str]:
    skills: set[str] = set()
    for path in staged:
        parts = path.parts
        for index, part in enumerate(parts):
            if part != "skills" or index == 0:
                continue
            if parts[index - 1] not in {".agents", ".claude"}:
                continue
            if index + 1 < len(parts):
                skills.add(parts[index + 1])
    return skills


def local_skill_parity_failures(skills: set[str]) -> list[str]:
    failures: list[str] = []
    for skill in sorted(skills):
        if skill not in LOCAL_DEVELOPMENT_SKILL_PARITY:
            continue
        codex_root = ROOT / ".agents" / "skills" / skill
        claude_root = ROOT / ".claude" / "skills" / skill
        if not codex_root.is_dir():
            failures.append(f"missing Codex development skill: {codex_root.relative_to(ROOT)}")
            continue
        if not claude_root.is_dir():
            failures.append(f"missing Claude development skill: {claude_root.relative_to(ROOT)}")
            continue
        codex_files = {
            path.relative_to(codex_root): path
            for path in codex_root.rglob("*")
            if path.is_file() and path.name != ".DS_Store"
        }
        claude_files = {
            path.relative_to(claude_root): path
            for path in claude_root.rglob("*")
            if path.is_file() and path.name != ".DS_Store"
        }
        for relpath in sorted(codex_files.keys() - claude_files.keys()):
            failures.append(f"{skill}: missing Claude parity file: {relpath}")
        for relpath in sorted(claude_files.keys() - codex_files.keys()):
            failures.append(f"{skill}: missing Codex parity file: {relpath}")
        for relpath in sorted(codex_files.keys() & claude_files.keys()):
            if codex_files[relpath].read_bytes() != claude_files[relpath].read_bytes():
                failures.append(f"{skill}: Codex/Claude development skill drift: {relpath}")
    return failures


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    print(f"[commit-gate] run {' '.join(command)}")
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def run_local_skill_parity(staged: list[Path]) -> tuple[str, int]:
    skills = touched_dev_skills(staged)
    if not skills:
        print("[commit-gate:local-skill-parity] SKIP")
        return "SKIP", 0
    failures = local_skill_parity_failures(skills)
    if failures:
        print("[commit-gate:local-skill-parity] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return "FAIL", 1
    print(f"[commit-gate:local-skill-parity] PASS skills={','.join(sorted(skills))}")
    return "PASS", 0


def append_filtered_files(command: list[str], staged: list[Path], gate: Gate) -> list[str]:
    if gate.file_filter is None:
        return command
    files = [str((ROOT / path).resolve()) for path in staged if gate.file_filter(path)]
    if not files:
        return command
    if "--paths" in command:
        insert_at = command.index("--paths") + 1
        return command[:insert_at] + files + command[insert_at:]
    return command + files


def run_shell_chain(command: list[str]) -> tuple[str, int]:
    parts: list[list[str]] = []
    current: list[str] = []
    for token in command:
        if token == "&&":
            if current:
                parts.append(current)
            current = []
        else:
            current.append(token)
    if current:
        parts.append(current)
    for part in parts:
        result = run_command(part)
        if result.stdout.strip():
            print(result.stdout.rstrip())
        if result.stderr.strip():
            print(result.stderr.rstrip(), file=sys.stderr)
        if result.returncode != 0:
            return "FAIL", result.returncode
    return "PASS", 0


def execute_gate(gate: Gate, staged: list[Path]) -> tuple[str, int]:
    if gate.gate_id == "local-skill-parity":
        return run_local_skill_parity(staged)

    if gate.matcher is not None and not gate.matcher(staged):
        return "SKIP", 0

    command = append_filtered_files(list(gate.command), staged, gate)
    if gate.file_filter is not None and command == gate.command:
        return "SKIP", 0

    if " && " in command or "&&" in command:
        return run_shell_chain(command)

    result = run_command(command)
    if result.stdout.strip():
        print(result.stdout.rstrip())
    if result.stderr.strip():
        print(result.stderr.rstrip(), file=sys.stderr)
    return ("PASS" if result.returncode == 0 else "FAIL"), result.returncode


def gate_plan() -> list[Gate]:
    surface_suffixes = {".json", ".yml", ".yaml", ".js", ".mjs", ".cjs", ".py"}
    code_suffixes = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".sh", ".ps1"}
    doc_suffixes = {".md", ".html", ".mdc"}
    text_suffixes = TEXT_SCAN_SUFFIXES

    return [
        Gate("reference-package", ["python3", "scripts/validate_reference_package.py", "--staged-only"]),
        Gate(
            "goal-maestro-walls",
            ["node", "src/adapters/claude/skills/tes-goal-maestro/scripts/validate-walls.mjs"],
            matcher=lambda paths: any_match(
                paths,
                ("*/skills/tes-goal-maestro/scripts/*.mjs",),
            ),
        ),
        # Part A residual (ADR 0006): move the two audit-leaked defect classes
        # (placeholder commits, stale anchor provenance) from audit-final to commit-time.
        # The ledger is the staged artifact that carries both signals.
        Gate(
            "goal-maestro-ledger-placeholder",
            ["node", "src/adapters/claude/skills/tes-goal-maestro/scripts/ledger-no-placeholder.mjs"],
            matcher=lambda paths: any_match(paths, ("GOAL-EXECUTION-LOOP-LEDGER-*.md", "**/GOAL-EXECUTION-LOOP-LEDGER-*.md")),
            file_filter=lambda path: fnmatch.fnmatch(path.name, "GOAL-EXECUTION-LOOP-LEDGER-*.md"),
        ),
        Gate(
            "goal-maestro-anchor-rehash",
            ["node", "src/adapters/claude/skills/tes-goal-maestro/scripts/anchor-rehash-staged.mjs"],
            matcher=lambda paths: any_match(paths, ("GOAL-EXECUTION-LOOP-LEDGER-*.md", "**/GOAL-EXECUTION-LOOP-LEDGER-*.md")),
            file_filter=lambda path: fnmatch.fnmatch(path.name, "GOAL-EXECUTION-LOOP-LEDGER-*.md"),
        ),
        Gate(
            "staged-surfaces",
            ["python3", "scripts/staged_surface_check.py"],
            matcher=lambda paths: suffix_match(paths, surface_suffixes),
            file_filter=lambda path: path.suffix.lower() in surface_suffixes,
        ),
        Gate(
            "code-documentation",
            ["python3", "scripts/code_documentation_oracle.py", "--paths"],
            matcher=lambda paths: suffix_match(paths, code_suffixes),
            file_filter=lambda path: path.suffix.lower() in code_suffixes,
        ),
        Gate(
            "private-vocabulary",
            ["python3", "scripts/private_vocabulary_oracle.py", "--paths"],
            matcher=lambda paths: suffix_match(paths, text_suffixes),
            file_filter=lambda path: path.suffix.lower() in text_suffixes,
        ),
        Gate(
            "public-docs",
            ["python3", "scripts/build_public_docs.py", "--check"],
            matcher=lambda paths: any_match(
                paths,
                (
                    "docs/i18n/**",
                    "docs/index.html",
                    "scripts/build_public_docs.py",
                    "package.json",
                    "docs/dist/**",
                ),
            ),
        ),
        Gate(
            "tds",
            ["python3", "scripts/validate_tds.py"],
            matcher=lambda paths: any_match(
                paths,
                ("docs/tds/**", "docs/INDEX.md", "scripts/validate_tds.py"),
            ),
        ),
        Gate(
            "doc-size",
            ["python3", "scripts/validate_doc_size.py", "--paths"],
            matcher=lambda paths: suffix_match(paths, doc_suffixes)
            and any_match(paths, ("docs/**", "src/**", "README.md", "AGENTS.md")),
            file_filter=lambda path: path.suffix.lower() in doc_suffixes,
        ),
        Gate(
            "context-mesh",
            ["python3", "scripts/context_mesh_plan.py"],
            matcher=lambda paths: any_match(
                paths,
                (
                    "benchmarks/context-mesh/**",
                    "docs/mesh/**",
                    "scripts/context_mesh_*.py",
                ),
            ),
        ),
        Gate(
            "field-reports",
            [
                "python3",
                "scripts/field_reports.py",
                "--self-test",
                "&&",
                "python3",
                "scripts/field_reports_github_oracle.py",
                "--self-test",
            ],
            matcher=lambda paths: any_match(
                paths,
                (
                    ".github/ISSUE_TEMPLATE/tes-field-report.yml",
                    ".github/workflows/field-report-governance.yml",
                    "scripts/field_reports.py",
                    "scripts/field_reports_*.py",
                ),
            ),
        ),
        Gate(
            "hook-audit-prompt",
            ["python3", "scripts/hook_audit_prompt_oracle.py", "--self-test"],
            matcher=lambda paths: any_match(
                paths,
                (
                    "docs/install/HOOK-AUDIT-PROMPT.md",
                    "scripts/hook_audit_prompt_oracle.py",
                    "package.json",
                ),
            ),
        ),
        Gate(
            "pretooluse-kernel",
            ["python3", "scripts/pretooluse_kernel_oracle.py"],
            matcher=lambda paths: any_match(
                paths,
                (
                    "scripts/pretooluse_kernel.py",
                    "scripts/pretooluse_kernel_oracle.py",
                    "scripts/pretooluse_session.py",
                    "scripts/pretooluse_session_oracle.py",
                    "scripts/tes_install.py",
                    "package.json",
                ),
            ),
        ),
        Gate(
            "pretooluse-contract",
            ["python3", "scripts/pretooluse_contract_oracle.py", "--self-test"],
            matcher=lambda paths: any_match(
                paths,
                (
                    "docs/architecture/PRETOOLUSE-CONTRACT.md",
                    "docs/architecture/INSTALLATION-FRAMEWORK.md",
                    "docs/install/HOOK-AUDIT-PROMPT.md",
                    "scripts/pretooluse_contract_oracle.py",
                    "scripts/staged_commit_gate.py",
                    "package.json",
                ),
            ),
        ),
        Gate(
            "pretooluse-session",
            ["python3", "scripts/pretooluse_session_oracle.py"],
            matcher=lambda paths: any_match(
                paths,
                (
                    "scripts/pretooluse_session.py",
                    "scripts/pretooluse_session_oracle.py",
                    "scripts/tes_install.py",
                    "package.json",
                ),
            ),
        ),
        Gate(
            "host-runtime-matrix",
            ["python3", "scripts/host_runtime_matrix_oracle.py", "--self-test"],
            matcher=lambda paths: any_match(
                paths,
                (
                    "scripts/pretooluse_kernel.py",
                    "scripts/pretooluse_kernel_oracle.py",
                    "scripts/pretooluse_session.py",
                    "scripts/pretooluse_session_oracle.py",
                    "scripts/tes_install.py",
                    "scripts/mantra_gate_pretooluse_oracle.py",
                    "scripts/host_runtime_matrix_oracle.py",
                    "docs/install/HOOK-AUDIT-PROMPT.md",
                    "package.json",
                ),
            ),
        ),
        Gate(
            "materialize",
            ["python3", "scripts/materialize_adapter.py", "all", "--check"],
            matcher=lambda paths: any_match(
                paths,
                ("src/adapters/**", "scripts/materialize_adapter.py"),
            ),
        ),
        Gate(
            "discipline-oracle",
            [
                "python3",
                "src/adapters/codex/skills/tes-engineering-discipline/scripts/discipline_oracle.py",
                "--self-test",
            ],
            matcher=lambda paths: any_match(
                paths,
                (
                    "AGENTS.md",
                    "src/adapters/codex/**",
                    "src/adapters/claude/**",
                    "src/adapters/cursor/**",
                    "docs/governance/**",
                ),
            ),
        ),
        Gate(
            "cortex-reflect",
            ["python3", "scripts/pre_commit_cortex.py"],
            matcher=lambda paths: any_match(
                paths,
                (
                    "docs/agents/cortex/**",
                    "scripts/cortex.py",
                    "scripts/cortex_*.py",
                ),
            ),
        ),
        Gate(
            "asset-transfer-packet",
            ["python3", "scripts/supervise_detectors/new_skill_without_packet.py", "--target", "."],
            matcher=lambda paths: any_match(paths, ("*/skills/*/SKILL.md",)),
        ),
        Gate("local-skill-parity", []),
        Gate("git-whitespace", ["git", "diff", "--check", "&&", "git", "diff", "--cached", "--check"]),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--plan", action="store_true", help="print gate plan without running")
    args = parser.parse_args()

    staged = git_staged_paths()
    if not staged:
        print("[commit-gate] SKIP no staged files")
        return 0

    gates = gate_plan()
    report: list[dict[str, object]] = []
    failures = 0
    for gate in gates:
        if args.plan:
            if gate.gate_id == "local-skill-parity":
                status = "RUN" if touched_dev_skills(staged) else "SKIP"
            elif gate.matcher is None:
                status = "RUN"
            else:
                status = "RUN" if gate.matcher(staged) else "SKIP"
            report.append({"gate": gate.gate_id, "status": status})
            continue
        status, code = execute_gate(gate, staged)
        report.append({"gate": gate.gate_id, "status": status})
        if status == "FAIL":
            failures += 1

    if args.plan:
        print(f"[commit-gate:plan] staged_files={len(staged)}")
        for item in report:
            print(f"- {item['gate']}: {item['status']}")
        return 0

    summary = {
        "version": VERSION,
        "status": "PASS" if failures == 0 else "FAIL",
        "staged_files": len(staged),
        "gates": report,
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"[commit-gate] {summary['status']} staged_files={summary['staged_files']}")
        for item in report:
            print(f"- {item['gate']}: {item['status']}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
