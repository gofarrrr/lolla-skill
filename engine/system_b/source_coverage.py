"""Deterministic source-preservation and processing-coverage metadata."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


SOURCE_COVERAGE_SCHEMA_VERSION = "lolla.source_coverage.v1"


def build_source_coverage(
    *,
    processing_view: Mapping[str, Any] | None,
    capture_adequacy: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Describe source preservation separately from initial extraction coverage.

    Unknown historical fields remain unknown. This function reports deterministic
    artifact custody only; it does not infer whether the processed view preserved
    the conversation's important meaning.
    """

    view = dict(processing_view or {})
    adequacy = dict(capture_adequacy or {})
    preserved = view.get("authoritative_conversation_preserved")
    return {
        "schema_version": SOURCE_COVERAGE_SCHEMA_VERSION,
        "authoritative_conversation_preserved": (
            bool(preserved) if preserved is not None else None
        ),
        "extraction_processing_view_status": _text(view.get("status")) or "unknown",
        "extraction_processing_strategy": (
            _text(view.get("processing_strategy")) or "unknown"
        ),
        "authoritative_turn_count": adequacy.get("declared_turn_count"),
        "extraction_processing_turn_count": adequacy.get("captured_turn_count"),
        "extraction_omitted_turn_count": adequacy.get("omitted_turn_count"),
    }


def _text(value: Any) -> str:
    return str(value or "").strip()
