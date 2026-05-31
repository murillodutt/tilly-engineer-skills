#!/usr/bin/env python3
"""Convert a PT-BR pronunciation dictionary into TES TTS JSONL manifest records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import unicodedata
from typing import TextIO


VERSION = "0.3.148"
DEFAULT_LANGUAGE = "pt-BR"
DEFAULT_SOURCE = "pt_br_prondict"
DEFAULT_LICENSE_NOTE = "public dictionary reference; provenance retained"
DEFAULT_USAGE = "evidence_only"
DEFAULT_STATUS = "reference"
DEFAULT_PRONUNCIATION_SYSTEM = "ipa"


def normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value.strip())


def parse_prondict_line(line: str, line_number: int) -> dict[str, str | int] | None:
    normalized = normalize_text(line)
    if not normalized or normalized.startswith("#"):
        return None
    parts = normalized.split(maxsplit=1)
    if len(parts) != 2:
        raise ValueError(f"line {line_number}: expected WORD<space>PRONUNCIATION")
    return {
        "line_number": line_number,
        "text_graphemes": normalize_text(parts[0]),
        "pronunciation": normalize_text(parts[1]),
    }


def manifest_record(
    parsed: dict[str, str | int],
    *,
    record_id: str,
    language: str,
    source: str,
    source_path: str,
    license_note: str,
    usage: str,
    status: str,
    pronunciation_system: str,
) -> dict[str, str | int]:
    return {
        "id": record_id,
        "language": language,
        "text_graphemes": parsed["text_graphemes"],
        "pronunciation": parsed["pronunciation"],
        "pronunciation_system": pronunciation_system,
        "source": source,
        "source_path": source_path,
        "source_line": parsed["line_number"],
        "license_note": license_note,
        "usage": usage,
        "status": status,
    }


def convert_prondict(
    input_path: Path,
    output: TextIO,
    *,
    id_prefix: str,
    language: str,
    source: str,
    source_path: str | None,
    license_note: str,
    usage: str,
    status: str,
    pronunciation_system: str,
    limit: int | None,
) -> int:
    count = 0
    source_path_value = source_path or str(input_path)
    with input_path.open("r", encoding="utf-8") as source_file:
        for line_number, line in enumerate(source_file, start=1):
            parsed = parse_prondict_line(line, line_number)
            if parsed is None:
                continue
            count += 1
            record = manifest_record(
                parsed,
                record_id=f"{id_prefix}-{count:06d}",
                language=language,
                source=source,
                source_path=source_path_value,
                license_note=license_note,
                usage=usage,
                status=status,
                pronunciation_system=pronunciation_system,
            )
            output.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            if limit is not None and count >= limit:
                break
    return count


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / "sample.dict"
        output_path = Path(tmpdir) / "sample.jsonl"
        input_path.write_text(
            "# comment\n"
            "ABACAXI\tˌabakaʃˈi\n"
            "A-PROPÓSITO\tapɾˌopˈɔzitʊ\n"
            "AÇÃO\tasˈɐ̃ʊ̃\n",
            encoding="utf-8",
        )
        with output_path.open("w", encoding="utf-8") as output:
            count = convert_prondict(
                input_path,
                output,
                id_prefix="ptbr-lexical",
                language=DEFAULT_LANGUAGE,
                source=DEFAULT_SOURCE,
                source_path=None,
                license_note=DEFAULT_LICENSE_NOTE,
                usage=DEFAULT_USAGE,
                status=DEFAULT_STATUS,
                pronunciation_system=DEFAULT_PRONUNCIATION_SYSTEM,
                limit=None,
            )
        records = [
            json.loads(line)
            for line in output_path.read_text(encoding="utf-8").splitlines()
        ]
    failures: list[str] = []
    if count != 3:
        failures.append(f"expected 3 records, got {count}")
    if records[0]["id"] != "ptbr-lexical-000001":
        failures.append("first id drifted")
    if records[1]["text_graphemes"] != "A-PROPÓSITO":
        failures.append("accented hyphenated grapheme drifted")
    if records[2]["pronunciation"] != "asˈɐ̃ʊ̃":
        failures.append("IPA pronunciation drifted")
    if any(record["usage"] != DEFAULT_USAGE for record in records):
        failures.append("usage must remain evidence_only")

    status = "FAIL" if failures else "PASS"
    print(json.dumps({"status": status, "version": VERSION, "failures": failures}, indent=2))
    print(f"[tes-tts-ptbr-prondict-to-manifest] {status}")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path, help="PT-BR prondict file to convert")
    parser.add_argument("output", nargs="?", type=Path, help="Output JSONL manifest path, or '-' for stdout")
    parser.add_argument("--id-prefix", default="ptbr-lexical")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE)
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--source-path", default=None)
    parser.add_argument("--license-note", default=DEFAULT_LICENSE_NOTE)
    parser.add_argument("--usage", default=DEFAULT_USAGE)
    parser.add_argument("--status", default=DEFAULT_STATUS)
    parser.add_argument("--pronunciation-system", default=DEFAULT_PRONUNCIATION_SYSTEM)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.input is None or args.output is None:
        parser.error("input and output are required unless --self-test is used")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be greater than zero")

    if str(args.output) == "-":
        count = convert_prondict(
            args.input,
            sys.stdout,
            id_prefix=args.id_prefix,
            language=args.language,
            source=args.source,
            source_path=args.source_path,
            license_note=args.license_note,
            usage=args.usage,
            status=args.status,
            pronunciation_system=args.pronunciation_system,
            limit=args.limit,
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as output:
            count = convert_prondict(
                args.input,
                output,
                id_prefix=args.id_prefix,
                language=args.language,
                source=args.source,
                source_path=args.source_path,
                license_note=args.license_note,
                usage=args.usage,
                status=args.status,
                pronunciation_system=args.pronunciation_system,
                limit=args.limit,
            )
    print(f"[tes-tts-ptbr-prondict-to-manifest] wrote {count} records", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
