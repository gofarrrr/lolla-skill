#!/usr/bin/env python3
"""Validate v4.1 and v4.2 schemas with the current google-genai native Schema model."""
from __future__ import annotations

import argparse
import copy
import importlib.metadata
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.genai import _transformers, types  # type: ignore[import-not-found]  # noqa: E402

from engine.system_b.reasoning_process_chronological_shard_reader_v41 import (  # noqa: E402
    shard_response_schema_v41,
)
from engine.system_b.reasoning_process_chronological_shard_reader_v42 import (  # noqa: E402
    shard_response_schema_v42,
)
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _native_validate(schema: dict) -> tuple[str, list[str]]:
    value = copy.deepcopy(schema)
    try:
        _transformers.process_schema(value, None)
        types.Schema.model_validate(value)
        return "pass", []
    except Exception as exc:  # noqa: BLE001
        errors = []
        if hasattr(exc, "errors"):
            for item in exc.errors():
                location = ".".join(str(part) for part in item.get("loc", ()))
                errors.append(f"{location}: {item.get('msg', '')}")
        if not errors:
            errors.append(f"{type(exc).__name__}: {exc}")
        return "fail", errors


def _keyword_count(value: object, keyword: str) -> int:
    if isinstance(value, dict):
        return (1 if keyword in value else 0) + sum(
            _keyword_count(child, keyword) for child in value.values()
        )
    if isinstance(value, list):
        return sum(_keyword_count(child, keyword) for child in value)
    return 0


def build() -> dict:
    v41 = shard_response_schema_v41("position_and_decision_trajectory")
    v42 = shard_response_schema_v42("position_and_decision_trajectory")
    v41_status, v41_errors = _native_validate(v41)
    v42_status, v42_errors = _native_validate(v42)
    return {
        "schema_version": "lolla.reasoning_process_stance_object_v42_google_schema_preflight.v1",
        "status": "pass" if v41_status == "fail" and v42_status == "pass" else "fail",
        "date": "2026-07-12",
        "sdk": {
            "package": "google-genai",
            "version": importlib.metadata.version("google-genai"),
            "validator": "google.genai.types.Schema_after_process_schema",
        },
        "v41": {
            "schema_sha256": sha256_bytes(canonical_json_bytes(v41)),
            "schema_metrics": schema_metrics(v41),
            "unique_items_keyword_count": _keyword_count(v41, "uniqueItems"),
            "native_schema_status": v41_status,
            "errors": v41_errors,
        },
        "v42": {
            "schema_sha256": sha256_bytes(canonical_json_bytes(v42)),
            "schema_metrics": schema_metrics(v42),
            "unique_items_keyword_count": _keyword_count(v42, "uniqueItems"),
            "native_schema_status": v42_status,
            "errors": v42_errors,
        },
        "change": {
            "prompt_changed": False,
            "semantic_fields_changed": False,
            "record_validator_changed": False,
            "removed_keyword": "uniqueItems",
            "removed_keyword_count": 3,
            "deterministic_duplicate_validation_retained": True,
        },
        "calls": {
            "provider": 0,
            "evaluator": 0,
            "embedding": 0,
            "graph": 0,
            "runtime": 0,
        },
        "nonclaim": "Native SDK acceptance is a provider compatibility preflight, not proof of provider acceptance or semantic correctness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build()
    _write(args.output.resolve(), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
