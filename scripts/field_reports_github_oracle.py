#!/usr/bin/env python3
"""Validate the GitHub receiver surface for TES Field Reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile

import field_reports


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.150"
DESTINATION_REPO = "murillodutt/tilly-engineer-skills"
SCHEMA = "tes-field-report@2"
MAX_BODY_CHARS = 48000
SYNTHETIC_USER_PATH = "/" + "Users/person/private.py"
SYNTHETIC_EMAIL = "person" + "@example.com"
SYNTHETIC_SECRET_VALUE = "abc" + "123"
SYNTHETIC_SECRET_ASSIGNMENT = "token=" + SYNTHETIC_SECRET_VALUE
SYNTHETIC_BEARER_SECRET = "Bearer " + SYNTHETIC_SECRET_VALUE
SYNTHETIC_PRIVATE_URL = "https://" + "private." + "example.test/repo"
SYNTHETIC_PRIVATE_REMOTE = "git@" + "github.com:private/repo.git"

REQUIRED_BODY_TERMS = (
    f"<!-- {SCHEMA} -->",
    "TES Field Report",
    f"- Schema: {SCHEMA}",
    f"- Destination: {DESTINATION_REPO}",
    "- Event count:",
    "- Material event count:",
    "- Report class:",
    "- Actionability:",
    "- Severity:",
    "- Product class:",
    "- Product classes:",
    "- Certification impact:",
    "- Owner surface:",
    "- Next action:",
    "- Privacy state:",
    "- Signal score:",
    "- Report fingerprint:",
    "- Dedupe fingerprint:",
    "- Install fingerprints:",
    "Actionable findings",
    "Events",
)

REQUIRED_FORM_TERMS = (
    "### Schema",
    SCHEMA,
    "### Status",
    "### Report class",
    "### Actionability",
    "### Severity",
    "### Product class",
    "### Product classes",
    "### Certification impact",
    "### Owner surface",
    "### Next action",
    "### Privacy state",
    "### Report fingerprint",
    "### Dedupe fingerprint",
    "### TES version",
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
    ("raw prompt", re.compile(r"(?im)^\s*(prompt|raw prompt)\s*:")),
    ("raw diff", re.compile(r"(?im)^\s*(diff|patch)\s*:|^\s*(\+\+\+|---|@@)\s")),
    ("raw code", re.compile(r"(?im)^\s*(code|content)\s*:|def\s+\w+\(|function\s+\w+\(")),
)


def validate_body(text: str, require_field_report: bool = False) -> dict[str, object]:
    if SCHEMA not in text and not text.lstrip().startswith("TES Field Report"):
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
            "reason": "not a TES Field Report",
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
    issue_form = ROOT / ".github/ISSUE_TEMPLATE/tes-field-report.yml"
    workflow = ROOT / ".github/workflows/field-report-governance.yml"

    if not issue_form.exists():
        failures.append("missing GitHub issue form")
    else:
        text = issue_form.read_text(encoding="utf-8")
        for term in (SCHEMA, "field-report", "privacy-sanitized", "Actionability", "Never include code"):
            if term not in text:
                failures.append(f"issue form missing {term}")

    if not workflow.exists():
        failures.append("missing GitHub governance workflow")
    else:
        text = workflow.read_text(encoding="utf-8")
        for term in (
            "issues:",
            "issues: write",
            "field_reports_github_oracle.py validate-body",
            "field-report-quarantine",
            "state_reason=not_planned",
            "Expected rejected TES Field Report to close",
        ):
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
    with tempfile.TemporaryDirectory(prefix="tes-field-github-") as tempdir:
        target = Path(tempdir)
        event = field_reports.build_event(target, "cortex.verify", "PASS", "cortex", "self-test")
        good_body = field_reports.build_issue_body([event], 1, 1)
        good = validate_body(good_body)
        if good["status"] != "PASS":
            failures.append("valid field report body must pass")
            failures.extend(str(item) for item in good.get("failures", []))

        bad_body = (
            good_body
            + "\n| leaked | table |\n"
            + SYNTHETIC_USER_PATH
            + "\n"
            + SYNTHETIC_SECRET_ASSIGNMENT
            + "\nTraceback (most recent call last):\n```python\n"
        )
        bad = validate_body(bad_body)
        if bad["status"] != "FAIL":
            failures.append("unsafe field report body must fail")

        negative_tails = {
            "missing schema": "TES Field Report\n- Event count: 1\n",
            "over-large body": good_body + ("x" * (MAX_BODY_CHARS + 1)),
            "code fence": good_body + "\n```python\nprint('x')\n```",
            "markdown table": good_body + "\n| leaked | table |\n",
            "absolute path": good_body + "\n" + SYNTHETIC_USER_PATH + "\n",
            "email": good_body + "\n" + SYNTHETIC_EMAIL + "\n",
            "private url": good_body + "\n" + SYNTHETIC_PRIVATE_URL + "\n",
            "secret": good_body + "\nAuthorization: " + SYNTHETIC_BEARER_SECRET + "\n",
            "git remote": good_body + "\n" + SYNTHETIC_PRIVATE_REMOTE + "\n",
            "branch": good_body + "\nbranch=feature/private-work\n",
            "stack trace": good_body + "\nTraceback (most recent call last):\n",
            "prompt": good_body + "\nPrompt: raw prompt text\n",
            "diff": good_body + "\nDiff: + leaked line\n",
            "code": good_body + "\nCode: def leaked_function(): pass\n",
            "unsafe tail": good_body + "\nAccepted header\n\n" + SYNTHETIC_USER_PATH + "\n",
        }
        for label, body in negative_tails.items():
            result = validate_body(body, require_field_report=(label == "missing schema"))
            if result["status"] != "FAIL":
                failures.append(f"unsafe receiver fixture must fail: {label}")

        ignored = validate_body("General user issue without Tilly schema.")
        if ignored["status"] != "IGNORE":
            failures.append("non-field-report issue must be ignored")
        required = validate_body("TES Field Report without schema.", True)
        if required["status"] != "FAIL":
            failures.append("required field report without schema must fail")

        form_body = "\n".join(
            (
                "### Schema",
                SCHEMA,
                "### Status",
                "PASS",
                "### Report class",
                "version-drift",
                "### Actionability",
                "high",
                "### Severity",
                "high",
                "### Product class",
                "version-drift",
                "### Product classes",
                "RELEASE_HYGIENE",
                "### Certification impact",
                "partial-certification",
                "### Owner surface",
                "release",
                "### Next action",
                "review update scope and release identity",
                "### Privacy state",
                "sanitized",
                "### Report fingerprint",
                "fpr-fixture-67890",
                "### Dedupe fingerprint",
                "fpr-fixture-67890",
                "### TES version",
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
