#!/usr/bin/env python3
"""Gemini-compatible wrapper for conversation-state extraction probe v2.

V1 is preserved exactly as executed. V2 changes one response-schema keyword:
the fixed schema version uses a one-value string enum instead of JSON Schema
``const``, which is absent from Google's documented structured-output subset.
All prompts, custody, stop, scoring, and authorization behavior remain in the
reviewed v1 runner.
"""
from __future__ import annotations

import copy
import sys
from collections.abc import Sequence
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.evals import run_conversation_state_extraction_probe as v1


_V1_RESPONSE_SCHEMA = v1.response_schema


def response_schema() -> dict:
    schema = copy.deepcopy(_V1_RESPONSE_SCHEMA())
    version = schema["schema"]["properties"]["schema_version"]
    fixed_value = version.pop("const")
    version["enum"] = [fixed_value]
    return schema


def main(argv: Sequence[str] | None = None) -> int:
    v1.response_schema = response_schema
    return v1.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
