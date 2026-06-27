#!/usr/bin/env python3
"""Certify the installed hook-audit prompt contract."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "docs/install/HOOK-AUDIT-PROMPT.md"
VERSION = "0.3.220"


REQUIRED_TERMS = (
    "This is a per-host native audit",
    "docs/architecture/PRETOOLUSE-CONTRACT.md",
    "floor contract (`PASS_BASIC`)",
    "ceiling contract (`PASS_CEILING`)",
    "Do not collapse `PASS` into `PASS_CEILING`.",
    "## Ceiling Assessment",
    "Do not fail the current run only because\nanother platform's native tool is unavailable",
    "CONFIGURED, OBSERVED from prior ledger records, CONTRACT_SIMULATED, or",
    "If this is an adopter target, mark that source gate\nN/A",
    "If the current Cursor host exposes StrReplace",
    "use\n  StrReplace for the second same-path mutation",
    "marker_emitted: true",
    "Before any native forbidden-shell test",
    "Do\nnot write helper scripts, audit harnesses, or payload files inside the target\nproject",
    "verify `apply_patch`, `Bash`,\n  `Shell`, and `shell`",
    "Codex `tool_input.command` is the canonical patch-body field",
    "defensive aliases `input`, `patch`, and `arguments.*`",
    "alias-key failures are findings",
    "if native `StrReplace` is observed or exposed",
    "governed\n  `StrReplace`",
    "must classify as material/supervised\n  rather than routine",
    "Report the native payload tool label",
    "redacted raw hook payload",
    "`tool: \"Write\"`",
    "not as a TES finding\n  when the row still has `risk=material`",
    "explicitly records `tool: \"StrReplace\"`",
    "treats it as\n  routine or silently non-governed",
    "Redact file content, secrets, and unrelated\n  payload fields",
    "Cursor reports must separate host payload\n  labeling from TES classification",
    "hook-entrypoint simulation with explicit `tool: \"StrReplace\"`",
    "Cursor `preToolUse` deny messages are\nagent-visible, but governed allow messages may be ledger-only in the native UI",
    "do not classify ledger-proven Cursor allow supervision as a finding solely\nbecause no visible allow banner was shown",
    "Do not place the forbidden token\nsequence in the outer shell command, heredoc, comment, label, or inline script",
    "construct it from fragments inside the payload\ngenerator or use a temp file created without contiguous forbidden text on the\ncommand line",
    "Treat repeated stable simulation ids with different\n  timestamps as replay history, not duplicate hook execution.",
    "duplicate\n  runtime hooks only when the same agent/event/invocation/decision/timestamp is\n  repeated identically",
    "For external dedup or analytics, do not key only on\n  invocation and timestamp",
    "include at least tool, risk, path or command, and\n  session/mode when present",
    "Cursor may batch multiple native tool projections\n  under the same invocation/timestamp",
    "not duplicates when\n  tool, path, risk, marker, or mode differ",
    "Hook-health split: JSON schema `tes-hook-health@2` keeps `status` as the\n  legacy functional field",
    "`floor_status`, `ceiling_status`, and\n  `ceiling_gaps`",
    "`floor_status=PASS_BASIC` is not `PASS_CEILING`",
    "`ceiling_status=PASS_CEILING` and no `ceiling_gaps` remain",
    "PreToolUse helper packaging: TES 0.3.218+ installs must include",
    "`.tes/bin/pretooluse_kernel.py` and `.tes/bin/pretooluse_session.py`, and both",
    "must import successfully from `.tes/bin`",
    "`helper_contract_status=PASS`",
    "CONTRACT_SIMULATED: host-specific contract was proven",
    "PASS_WITH_FINDINGS allowance is closed and narrow",
    "When hook-health JSON exposes `dedupe_contract`",
    "host, tool, risk, path or command category, session, mode, and marker state",
    "`same_semantic_different_timestamp_is_replay_history`",
    "`same_invocation_timestamp_different_tool_path_risk_marker_is_not_duplicate`",
    "`NEEDS_DISCOVERABILITY`: host payload semantics or a new tool name are safe",
    "Runtime\n  output must include `outcome=needs_discoverability`",
    "`risk=needs-discoverability`; the source matrix output must report\n  `discoverability_status=NEEDS_DISCOVERABILITY`",
    "`classifier_trace.unknown_mutating=true`",
    "`renderer_trace.output_contract`",
    "redacted payload evidence (`command_category`, not raw `command`)",
    "Ceiling evidence checklist: before reporting `PASS_CEILING`",
    "evidence names `reason_codes`, `classifier_trace`, `renderer_trace`",
    "`command_redacted=true` or `command_category`, `dedupe_contract`",
    "`helper_contract_status=PASS`, `floor_status`, `ceiling_status`",
    "`ceiling_gaps`, and `discoverability_status=NEEDS_DISCOVERABILITY` or native\nequivalent",
    "Missing checklist item is a ceiling gap, not a floor failure.",
    "Missing current-host native\nPreToolUse, matcher gaps, or execution of a forbidden command is FAIL",
)

FORBIDDEN_TERMS = (
    "all hosts must be native in one execution",
    "Mark FAIL if Codex, Claude, and Cursor are not all OBSERVED natively in this execution.",
    "fail the current run because another platform's native tool is unavailable",
)


@dataclass(frozen=True)
class Mutation:
    name: str
    text: str
    expected_fragment: str


def validate_text(text: str) -> list[str]:
    failures: list[str] = []
    for term in REQUIRED_TERMS:
        if term not in text:
            failures.append(f"missing required hook-audit prompt term: {term!r}")
    for term in FORBIDDEN_TERMS:
        if term in text:
            failures.append(f"forbidden hook-audit prompt term present: {term!r}")
    return failures


def _remove(text: str, term: str) -> str:
    if term not in text:
        return text
    return text.replace(term, "", 1)


def red_capability_mutations(text: str) -> list[Mutation]:
    return [
        Mutation(
            "without_per_host_native_contract",
            _remove(text, "This is a per-host native audit"),
            "per-host native audit",
        ),
        Mutation(
            "without_canonical_pretooluse_contract",
            _remove(text, "docs/architecture/PRETOOLUSE-CONTRACT.md"),
            "PRETOOLUSE-CONTRACT",
        ),
        Mutation(
            "without_pass_basic_status",
            _remove(text, "floor contract (`PASS_BASIC`)"),
            "PASS_BASIC",
        ),
        Mutation(
            "without_pass_ceiling_status",
            _remove(text, "ceiling contract (`PASS_CEILING`)"),
            "PASS_CEILING",
        ),
        Mutation(
            "without_no_pass_to_ceiling_collapse",
            _remove(text, "Do not collapse `PASS` into `PASS_CEILING`."),
            "PASS_CEILING",
        ),
        Mutation(
            "without_ceiling_assessment_section",
            _remove(text, "## Ceiling Assessment"),
            "Ceiling Assessment",
        ),
        Mutation(
            "without_contract_simulated_evidence_class",
            _remove(text, "CONTRACT_SIMULATED: host-specific contract was proven"),
            "CONTRACT_SIMULATED",
        ),
        Mutation(
            "without_codex_shell_matcher_terms",
            _remove(text, "verify `apply_patch`, `Bash`,\n  `Shell`, and `shell`"),
            "apply_patch",
        ),
        Mutation(
            "without_marker_ledger_proof",
            _remove(text, "marker_emitted: true"),
            "marker_emitted",
        ),
        Mutation(
            "without_no_target_harness_rule",
            _remove(text, "Do\nnot write helper scripts, audit harnesses, or payload files inside the target\nproject"),
            "helper scripts",
        ),
        Mutation(
            "without_codex_patch_alias_contract",
            _remove(text, "defensive aliases `input`, `patch`, and `arguments.*`"),
            "defensive aliases",
        ),
        Mutation(
            "without_cursor_allow_ledger_only_contract",
            _remove(text, "Cursor `preToolUse` deny messages are\nagent-visible, but governed allow messages may be ledger-only in the native UI"),
            "Cursor",
        ),
        Mutation(
            "without_cursor_allow_not_finding_contract",
            _remove(text, "do not classify ledger-proven Cursor allow supervision as a finding solely\nbecause no visible allow banner was shown"),
            "visible allow banner",
        ),
        Mutation(
            "without_forbidden_outer_command_guard",
            _remove(text, "Do not place the forbidden token\nsequence in the outer shell command, heredoc, comment, label, or inline script"),
            "forbidden token",
        ),
        Mutation(
            "without_forbidden_fragment_payload_guard",
            _remove(text, "construct it from fragments inside the payload\ngenerator or use a temp file created without contiguous forbidden text on the\ncommand line"),
            "fragments",
        ),
        Mutation(
            "without_replay_history_contract",
            _remove(text, "Treat repeated stable simulation ids with different\n  timestamps as replay history, not duplicate hook execution."),
            "replay history",
        ),
        Mutation(
            "without_duplicate_timestamp_contract",
            _remove(text, "duplicate\n  runtime hooks only when the same agent/event/invocation/decision/timestamp is\n  repeated identically"),
            "duplicate",
        ),
        Mutation(
            "without_external_dedup_key_warning",
            _remove(text, "For external dedup or analytics, do not key only on\n  invocation and timestamp"),
            "external dedup",
        ),
        Mutation(
            "without_external_dedup_fields",
            _remove(text, "include at least tool, risk, path or command, and\n  session/mode when present"),
            "tool, risk",
        ),
        Mutation(
            "without_cursor_batched_projection_note",
            _remove(text, "Cursor may batch multiple native tool projections\n  under the same invocation/timestamp"),
            "Cursor",
        ),
        Mutation(
            "without_non_duplicate_differing_fields",
            _remove(text, "not duplicates when\n  tool, path, risk, marker, or mode differ"),
            "not duplicates",
        ),
        Mutation(
            "without_cursor_strreplace_native_requirement",
            _remove(text, "If the current Cursor host exposes StrReplace"),
            "StrReplace",
        ),
        Mutation(
            "without_cursor_strreplace_material_classification",
            _remove(text, "must classify as material/supervised\n  rather than routine"),
            "material/supervised",
        ),
        Mutation(
            "without_cursor_native_payload_label_requirement",
            _remove(text, "Report the native payload tool label"),
            "native payload tool label",
        ),
        Mutation(
            "without_cursor_write_label_not_finding_contract",
            _remove(text, "not as a TES finding\n  when the row still has `risk=material`"),
            "risk=material",
        ),
        Mutation(
            "without_cursor_explicit_strreplace_failure_condition",
            _remove(text, "explicitly records `tool: \"StrReplace\"`"),
            "StrReplace",
        ),
        Mutation(
            "without_cursor_routine_failure_condition",
            _remove(text, "treats it as\n  routine or silently non-governed"),
            "routine",
        ),
        Mutation(
            "without_cursor_payload_redaction_requirement",
            _remove(text, "Redact file content, secrets, and unrelated\n  payload fields"),
            "Redact",
        ),
        Mutation(
            "without_cursor_payload_vs_classification_split",
            _remove(text, "Cursor reports must separate host payload\n  labeling from TES classification"),
            "host payload",
        ),
        Mutation(
            "without_cursor_explicit_strreplace_simulation",
            _remove(text, "hook-entrypoint simulation with explicit `tool: \"StrReplace\"`"),
            "hook-entrypoint",
        ),
        Mutation(
            "without_hook_health_v2_split",
            _remove(text, "Hook-health split: JSON schema `tes-hook-health@2` keeps `status` as the\n  legacy functional field"),
            "tes-hook-health@2",
        ),
        Mutation(
            "without_hook_health_floor_ceiling_fields",
            _remove(text, "`floor_status`, `ceiling_status`, and\n  `ceiling_gaps`"),
            "floor_status",
        ),
        Mutation(
            "without_hook_health_basic_not_ceiling",
            _remove(text, "`floor_status=PASS_BASIC` is not `PASS_CEILING`"),
            "PASS_BASIC",
        ),
        Mutation(
            "without_hook_health_ceiling_gap_rule",
            _remove(text, "`ceiling_status=PASS_CEILING` and no `ceiling_gaps` remain"),
            "ceiling_status",
        ),
        Mutation(
            "without_pretooluse_helper_packaging_contract",
            _remove(text, "PreToolUse helper packaging: TES 0.3.218+ installs must include"),
            "PreToolUse helper packaging",
        ),
        Mutation(
            "without_pretooluse_helper_paths",
            _remove(text, "`.tes/bin/pretooluse_kernel.py` and `.tes/bin/pretooluse_session.py`, and both"),
            "pretooluse_kernel",
        ),
        Mutation(
            "without_pretooluse_helper_import_contract",
            _remove(text, "must import successfully from `.tes/bin`"),
            ".tes/bin",
        ),
        Mutation(
            "without_pretooluse_helper_contract_status",
            _remove(_remove(text, "`helper_contract_status=PASS`"), "`helper_contract_status=PASS`"),
            "helper_contract_status",
        ),
        Mutation(
            "open_pass_with_findings_allowance",
            _remove(text, "PASS_WITH_FINDINGS allowance is closed and narrow"),
            "PASS_WITH_FINDINGS allowance",
        ),
        Mutation(
            "without_dedupe_contract_audit",
            _remove(text, "When hook-health JSON exposes `dedupe_contract`"),
            "dedupe_contract",
        ),
        Mutation(
            "without_dedupe_field_audit",
            _remove(text, "host, tool, risk, path or command category, session, mode, and marker state"),
            "host, tool",
        ),
        Mutation(
            "without_dedupe_replay_rule",
            _remove(text, "`same_semantic_different_timestamp_is_replay_history`"),
            "same_semantic",
        ),
        Mutation(
            "without_dedupe_cursor_batch_rule",
            _remove(text, "`same_invocation_timestamp_different_tool_path_risk_marker_is_not_duplicate`"),
            "same_invocation",
        ),
        Mutation(
            "without_needs_discoverability_status",
            _remove(text, "`NEEDS_DISCOVERABILITY`: host payload semantics or a new tool name are safe"),
            "NEEDS_DISCOVERABILITY",
        ),
        Mutation(
            "without_discoverability_runtime_output",
            _remove(text, "Runtime\n  output must include `outcome=needs_discoverability`"),
            "outcome=needs_discoverability",
        ),
        Mutation(
            "without_discoverability_matrix_status",
            _remove(
                text,
                "`risk=needs-discoverability`; the source matrix output must report\n  `discoverability_status=NEEDS_DISCOVERABILITY`",
            ),
            "discoverability_status",
        ),
        Mutation(
            "without_discoverability_classifier_trace",
            _remove(text, "`classifier_trace.unknown_mutating=true`"),
            "classifier_trace",
        ),
        Mutation(
            "without_discoverability_renderer_trace",
            _remove(text, "`renderer_trace.output_contract`"),
            "renderer_trace",
        ),
        Mutation(
            "without_discoverability_redacted_payload_evidence",
            _remove(text, "redacted payload evidence (`command_category`, not raw `command`)"),
            "command_category",
        ),
        Mutation(
            "without_ceiling_evidence_checklist",
            _remove(text, "Ceiling evidence checklist: before reporting `PASS_CEILING`"),
            "Ceiling evidence checklist",
        ),
        Mutation(
            "without_ceiling_checklist_trace_fields",
            _remove(text, "evidence names `reason_codes`, `classifier_trace`, `renderer_trace`"),
            "classifier_trace",
        ),
        Mutation(
            "without_ceiling_checklist_redaction_analytics",
            _remove(text, "`command_redacted=true` or `command_category`, `dedupe_contract`"),
            "command_redacted",
        ),
        Mutation(
            "without_ceiling_checklist_helper_floor_ceiling",
            _remove(text, "`helper_contract_status=PASS`, `floor_status`, `ceiling_status`"),
            "helper_contract_status",
        ),
        Mutation(
            "without_ceiling_checklist_discoverability",
            _remove(
                text,
                "`ceiling_gaps`, and `discoverability_status=NEEDS_DISCOVERABILITY` or native\nequivalent",
            ),
            "discoverability_status",
        ),
        Mutation(
            "without_ceiling_gap_not_floor_failure",
            _remove(text, "Missing checklist item is a ceiling gap, not a floor failure."),
            "ceiling gap",
        ),
        Mutation(
            "all_hosts_native_false_fail",
            text
            + "\nMark FAIL if Codex, Claude, and Cursor are not all OBSERVED natively in this execution.\n",
            "forbidden hook-audit prompt term present",
        ),
    ]


def self_test() -> dict[str, object]:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    failures = validate_text(text)
    red_failures: list[str] = []
    for mutation in red_capability_mutations(text):
        mutated_failures = validate_text(mutation.text)
        if not mutated_failures:
            red_failures.append(f"{mutation.name}: mutant unexpectedly passed")
            continue
        if not any(mutation.expected_fragment in failure for failure in mutated_failures):
            red_failures.append(
                f"{mutation.name}: expected failure containing {mutation.expected_fragment!r}, "
                f"got {mutated_failures!r}"
            )
    status = "PASS" if not failures and not red_failures else "FAIL"
    return {
        "version": VERSION,
        "status": status,
        "prompt": str(PROMPT_PATH.relative_to(ROOT)),
        "failures": failures,
        "red_capability_failures": red_failures,
        "mutants_checked": len(red_capability_mutations(text)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    report = self_test()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
