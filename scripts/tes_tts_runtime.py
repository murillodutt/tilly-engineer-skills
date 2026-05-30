#!/usr/bin/env python3
"""Dependency-free TES TTS runtime CLI.

The runtime pipeline is implemented in focused modules:
classifier -> verbalizer -> adapter. This file stays as the stable CLI and
compatibility facade for oracles and skills.
"""

from __future__ import annotations

import argparse
import json
import sys

from tes_tts_runtime_adapter import adapt_plain_text, prepare_spoken_text
from tes_tts_runtime_classifier import (
    classify_text,
    compile_index,
    match_spans,
    redact_secret_like_values,
)
from tes_tts_runtime_types import REDACTION_TOKEN, VERSION
from tes_tts_runtime_verbalizer import verbalize_ir


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare TES TTS spoken text and IR.")
    parser.add_argument("--text", required=True)
    parser.add_argument("--locale", default="pt-BR")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    result = prepare_spoken_text(args.text, args.locale)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
