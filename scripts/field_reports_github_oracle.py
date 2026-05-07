#!/usr/bin/env python3
"""Validate the GitHub receiver surface for Tilly Field Reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile

import field_reports


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.22"
DESTINATION_REPO = "murillodutt/tilly-engineer-skills"
SCHEMA = "tilly-field-report@1"
MAX_BODY_CHARS = 48000

REQUIRED_BODY_TERMS = (
    f"<!-- {SCHEMA} -->",
    "Tilly Field Report",
    f"- Schema: {SCHEMA}",
    f"- Destination: {DESTINATION_REPO}",
    "- Event count:",
    "Events",
)

REQUIRED_FORM_TERMS = (
    "### Schema",
    SCHEMA,
    "### Status",
    "### Tilly version",
    "### Sanitized facts",
    "### Privacy confirmation",
)

FORBIDDEN_PATTERNS = (
    ("code fence", re.compile(r"```")),
    ("markdown table", re.compile(r"(?m)^\s*\|.+\|\s*$")),
    ("absolute path", re.compile(r"(/Users|/home|/private|/var/folders|[A-Za-z]:\\)[^\s`\"')]+")),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("private url", re.compile(r"https?://(?!github\.com/murillodutt/tilly-engineer-skills/issues/)[^\s`\"')]+")),
    ("secret", re.compile(r"(?i)(api[_-]?key|authorization|bearer|credential|password|secret|token)\s*[:=]\s*[A-Za-z0-9._:/+=-]+")),
    ("git remote", re.compile(r"(?i)(github\.com[:/][^\s]+\.git|git@[^:\s]+:[^\s]+)")),
    ("branch name", re.compile(r"(?i)\b(branch|ref)\s*[:=]\s*[^\s]+")),
    ("stack trace", re.compile(r"(?i)(traceback \(most recent call last\)|\bat .+:\d+:\d+|exception: .+)")),
)


def validate_body(text: str, require_field_report: bool = False) -> dict[str, object]:
    if SCHEMA not in text and not text.lstrip().startswith("Tilly Field Report"):
        if require_field_report:
            return {
                "version": VERSION,
                "status": "FAIL",
                "schema": SCHEMA,
                "labels": ["field-report", "field-report-quarantine"],
                "failures": [f"missing required schema marker: {SCHEMA}"],
            }
        return {
            "version": VERSION,
            "status": "IGNORE",
            "reason": "not a Tilly Field Report",
            "labels": [],
            "failures": [],
        }

    failures: list[str] = []
    if len(text) > MAX_BODY_CHARS:
        failures.append(f"body exceeds {MAX_BODY_CHARS} characters")
    required_terms = REQUIRED_FORM_TERMS if "### Schema" in text else REQUIRED_BODY_TERMS
    for term in required_terms:
        if term not in text:
            failures.append(f"missing required term: {term}")
    for name, pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            failures.append(f"forbidden content: {name}")

    return {
        "version": VERSION,
        "status": "PASS" if not failures else "FAIL",
        "schema": SCHEMA,
        "labels": ["field-report", "privacy-sanitized"] if not failures else ["field-report", "field-report-quarantine"],
        "failures": failures,
    }


def github_receiver_contract() -> list[str]:
    failures: list[str] = []
    issue_form = ROOT / ".github/ISSUE_TEMPLATE/tilly-field-report.yml"
    workflow = ROOT / ".github/workflows/field-report-governance.yml"

    if not issue_form.exists():
        failures.append("missing GitHub issue form")
    else:
        text = issue_form.read_text(encoding="utf-8")
        for term in (SCHEMA, "field-report", "privacy-sanitized", "Never include code"):
            if term not in text:
                failures.append(f"issue form missing {term}")

    if not workflow.exists():
        failures.append("missing GitHub governance workflow")
    else:
        text = workflow.read_text(encoding="utf-8")
        for term in ("issues:", "issues: write", "field_reports_github_oracle.py validate-body", "field-report-quarantine"):
            if term not in text:
                failures.append(f"governance workflow missing {term}")

    return failures


def write_github_output(path: Path, result: dict[str, object]) -> None:
    labels = ",".join(str(item) for item in result.get("labels", []))
    failures = "; ".join(str(item) for item in result.get("failures", [])) or str(result.get("reason", ""))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"status={result.get('status', 'FAIL')}\n")
        handle.write(f"labels={labels}\n")
        handle.write(f"reason={failures[:500]}\n")


def self_test() -> dict[str, object]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="tilly-field-github-") as tempdir:
        target = Path(tempdir)
        event = field_reports.build_event(target, "cortex.verify", "PASS", "cortex", "self-test")
        good_body = field_reports.build_issue_body([event], 1, 1)
        good = validate_body(good_body)
        if good["status"] != "PASS":
            failures.append("valid field report body must pass")
            failures.extend(str(item) for item in good.get("failures", []))

        bad_body = good_body + "\n| leaked | table |\n/Users/person/private.py\ntoken=abc123\nTraceback (most recent call last):\n```python\n"
        bad = validate_body(bad_body)
        if bad["status"] != "FAIL":
            failures.append("unsafe field report body must fail")

        ignored = validate_body("General user issue without Tilly schema.")
        if ignored["status"] != "IGNORE":
            failures.append("non-field-report issue must be ignored")
        required = validate_body("Tilly Field Report without schema.", True)
        if required["status"] != "FAIL":
            failures.append("required field report without schema must fail")

        form_body = "\n".join(
            (
                "### Schema",
                SCHEMA,
                "### Status",
                "PASS",
                "### Tilly version",
                VERSION,
                "### Sanitized facts",
                "- event=cortex.verify",
                "### Privacy confirmation",
                "- [x] This report contains no prohibited content.",
            )
        )
        form = validate_body(form_body)
        if form["status"] != "PASS":
            failures.append("valid GitHub issue form body must pass")
            failures.extend(str(item) for item in form.get("failures", []))

    failures.extend(github_receiver_contract())
    return {"version": VERSION, "status": "PASS" if not failures else "FAIL", "failures": failures}


def print_result(result: dict[str, object]) -> int:
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"[field-reports-github] {result.get('status', 'FAIL')}")
    return 1 if result.get("status") == "FAIL" else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=("validate-body",))
    parser.add_argument("--body-file", type=Path)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--require-field-report", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return print_result(self_test())
    if args.command == "validate-body":
        if not args.body_file:
            parser.error("validate-body requires --body-file")
        result = validate_body(args.body_file.read_text(encoding="utf-8"), args.require_field_report)
        if args.github_output:
            write_github_output(args.github_output, result)
        print(json.dumps(result, indent=2, sort_keys=True))
        if args.strict and result.get("status") == "FAIL":
            return 1
        return 0
    parser.error("command is required unless --self-test is used")


if __name__ == "__main__":
    sys.exit(main())
