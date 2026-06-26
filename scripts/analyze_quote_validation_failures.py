#!/usr/bin/env python3
"""Analyze quote-validation failures from PR22 findings.

The CLI reads PR22's privacy-bounded findings JSON to identify affected
archive records, then inspects only those local archive folders. Raw transcript
and fabricated-passage text are used internally for deterministic diagnostics
but are never written to the Markdown or JSON outputs.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


class InputError(ValueError):
    """Deterministic, sanitized user-facing input error."""


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.quote_validation_diagnostics import (
        build_quote_validation_diagnostic_record,
        build_quote_validation_findings,
        render_quote_validation_findings_json,
        render_quote_validation_findings_markdown,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Classify quote-validation failures from a PR22 findings JSON. "
            "This is a local-only diagnostic and does not alter runtime quote validation."
        )
    )
    parser.add_argument("archive_root", type=Path)
    parser.add_argument("--findings-json", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path, help="Markdown report path.")
    parser.add_argument("--json-out", required=True, type=Path, help="JSON report path.")
    args = parser.parse_args(argv)

    try:
        findings_payload = _load_json_object(args.findings_json, "findings-json")
        affected = _quote_fabrication_records(findings_payload)
        archive_root = args.archive_root.expanduser()
        records = [
            build_quote_validation_diagnostic_record(
                archive_root / relpath,
                archive_root=archive_root,
            )
            for relpath in affected
        ]
        findings = build_quote_validation_findings(records)
        _write_text(args.out, render_quote_validation_findings_markdown(findings))
        _write_text(args.json_out, render_quote_validation_findings_json(findings))
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError(f"{label} is not valid JSON") from exc
    except OSError as exc:
        raise InputError(f"{label} could not be read:{type(exc).__name__}") from exc
    if not isinstance(payload, dict):
        raise InputError(f"{label} is not a JSON object")
    return payload


def _quote_fabrication_records(findings: Mapping[str, Any]) -> list[Path]:
    patterns = _mapping(findings.get("quote_fabrication_patterns"))
    raw_records = patterns.get("records")
    if not isinstance(raw_records, list):
        raise InputError("findings-json missing quote_fabrication_patterns.records")
    relpaths: list[Path] = []
    seen: set[str] = set()
    for item in raw_records:
        record = _mapping(item)
        relpath = _relative_record_path(record)
        key = str(relpath)
        if key not in seen:
            relpaths.append(relpath)
            seen.add(key)
    return sorted(relpaths, key=lambda path: str(path))


def _relative_record_path(record: Mapping[str, Any]) -> Path:
    relpath = _text(record.get("archive_relpath"))
    case_id = _text(record.get("case_id"))
    run_id = _text(record.get("run_id"))
    if not relpath:
        relpath = f"{case_id}/{run_id}"
    candidate = Path(relpath)
    if candidate.is_absolute() or ".." in candidate.parts:
        if not case_id or not run_id:
            raise InputError("findings-json contains unsafe archive_relpath")
        candidate = Path(case_id) / run_id
    if not candidate.parts:
        raise InputError("findings-json contains empty archive_relpath")
    return candidate


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any) -> str:
    return str(value or "").strip()


if __name__ == "__main__":
    raise SystemExit(main())
