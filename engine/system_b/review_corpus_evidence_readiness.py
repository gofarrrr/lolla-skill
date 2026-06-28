"""Readiness analysis for review-corpus high-stakes evidence.

This module reads only review-corpus manifest metadata. It does not inspect
archive folders, transcript text, memos, revised answers, model/provider text,
or private reasoning.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


REVIEW_CORPUS_EVIDENCE_READINESS_SCHEMA_VERSION = (
    "lolla.review_corpus_evidence_readiness.v0"
)

REQUIRED_MANIFEST_FIELDS = (
    "record_count",
    "risk_mode_counts",
    "risk_mode_reliance_present_counts",
    "risk_mode_reliance_by_risk_mode_counts",
    "risk_mode_reliance_check_status_counts",
)

EVIDENCE_STATES = (
    "no_high_stakes_reliance_evidence",
    "has_high_stakes_reliance_evidence",
    "insufficient_manifest_fields",
)

RECOMMENDATIONS = (
    "do_not_claim_high_stakes_archive_evidence",
    "ready_for_high_stakes_review_batch",
)


class InputError(ValueError):
    """Deterministic, sanitized input error."""


def load_manifest(path: Path | str) -> dict[str, Any]:
    """Load a review-corpus manifest JSON object."""

    manifest_path = Path(path)
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError("manifest is not valid JSON") from exc
    except OSError as exc:
        raise InputError(f"manifest could not be read:{type(exc).__name__}") from exc
    if not isinstance(payload, dict):
        raise InputError("manifest is not a JSON object")
    return payload


def build_evidence_readiness(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic readiness report from a review-corpus manifest."""

    missing_fields = [
        field
        for field in REQUIRED_MANIFEST_FIELDS
        if not _manifest_field_available(manifest, field)
    ]
    record_count = _safe_int(manifest.get("record_count"))
    risk_mode_counts = _count_mapping(manifest.get("risk_mode_counts"))
    reliance_present_counts = _boolean_counts(
        manifest.get("risk_mode_reliance_present_counts")
    )
    reliance_by_risk_mode_counts = _count_mapping(
        manifest.get("risk_mode_reliance_by_risk_mode_counts")
    )
    reliance_check_status_counts = _count_mapping(
        manifest.get("risk_mode_reliance_check_status_counts")
    )
    high_stakes_reliance_present_count = _safe_int(
        reliance_by_risk_mode_counts.get("high_stakes|true")
    )

    if missing_fields:
        evidence_state = "insufficient_manifest_fields"
        recommendation = "do_not_claim_high_stakes_archive_evidence"
    elif high_stakes_reliance_present_count > 0:
        evidence_state = "has_high_stakes_reliance_evidence"
        recommendation = "ready_for_high_stakes_review_batch"
    else:
        evidence_state = "no_high_stakes_reliance_evidence"
        recommendation = "do_not_claim_high_stakes_archive_evidence"

    return {
        "schema_version": REVIEW_CORPUS_EVIDENCE_READINESS_SCHEMA_VERSION,
        "source": {
            "local_only": True,
            "manifest_read": True,
            "manifest_path_included": False,
            "archive_root_included": False,
            "raw_archives_read": False,
            "raw_transcript_included": False,
            "raw_memo_included": False,
            "raw_revised_answer_included": False,
            "raw_model_message_content_included": False,
            "provider_reasoning_details_included": False,
            "private_reasoning_included": False,
            "model_calls": 0,
            "llm_judge_used": False,
        },
        "manifest_schema_version": _text(manifest.get("schema_version")),
        "record_schema_version": _text(manifest.get("record_schema_version")),
        "record_count": record_count,
        "risk_mode_counts": risk_mode_counts,
        "risk_mode_reliance_present_counts": reliance_present_counts,
        "risk_mode_reliance_by_risk_mode_counts": reliance_by_risk_mode_counts,
        "risk_mode_reliance_check_status_counts": reliance_check_status_counts,
        "high_stakes_reliance_present_count": high_stakes_reliance_present_count,
        "missing_manifest_fields": missing_fields,
        "evidence_state": evidence_state,
        "recommendation": recommendation,
        "caveats": _caveats(
            missing_fields=missing_fields,
            reliance_present_counts=reliance_present_counts,
            high_stakes_reliance_present_count=high_stakes_reliance_present_count,
        ),
    }


def render_evidence_readiness_markdown(readiness: Mapping[str, Any]) -> str:
    """Render a compact Markdown readiness report."""

    missing_fields = _strings(readiness.get("missing_manifest_fields"))
    lines = [
        "# Review Corpus Evidence Readiness",
        "",
        "## Summary",
        "",
        f"- Evidence state: `{_text(readiness.get('evidence_state'))}`",
        f"- Recommendation: `{_text(readiness.get('recommendation'))}`",
        f"- Records: `{_safe_int(readiness.get('record_count'))}`",
        (
            "- High-stakes reliance-present records: "
            f"`{_safe_int(readiness.get('high_stakes_reliance_present_count'))}`"
        ),
        f"- Risk modes: {_format_counts(readiness.get('risk_mode_counts'))}",
        (
            "- Reliance present counts: "
            f"{_format_counts(readiness.get('risk_mode_reliance_present_counts'))}"
        ),
        (
            "- Reliance by risk mode: "
            f"{_format_counts(readiness.get('risk_mode_reliance_by_risk_mode_counts'))}"
        ),
        (
            "- Reliance check statuses: "
            f"{_format_counts(readiness.get('risk_mode_reliance_check_status_counts'))}"
        ),
        "",
        "## Missing Manifest Fields",
        "",
    ]
    if missing_fields:
        lines.extend(f"- `{field}`" for field in missing_fields)
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Caveats",
            "",
        ]
    )
    caveats = _strings(readiness.get("caveats"))
    if caveats:
        lines.extend(f"- {caveat}" for caveat in caveats)
    else:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def render_evidence_readiness_json(readiness: Mapping[str, Any]) -> str:
    """Render deterministic JSON readiness output."""

    return json.dumps(readiness, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_text(path: Path | str, payload: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")


def _manifest_field_available(manifest: Mapping[str, Any], field: str) -> bool:
    if field not in manifest:
        return False
    value = manifest.get(field)
    if field == "record_count":
        return isinstance(value, int)
    return isinstance(value, Mapping)


def _caveats(
    *,
    missing_fields: list[str],
    reliance_present_counts: Mapping[str, int],
    high_stakes_reliance_present_count: int,
) -> list[str]:
    if missing_fields:
        return [
            "Manifest does not contain the PR44 reliance aggregate fields; do not infer high-stakes evidence from older manifest shape."
        ]
    if high_stakes_reliance_present_count <= 0:
        return [
            "No high-stakes reliance-present archive evidence is visible in this manifest."
        ]
    if _safe_int(reliance_present_counts.get("true")) <= 0:
        return [
            "High-stakes reliance count is inconsistent with total reliance-present count."
        ]
    return [
        "High-stakes reliance-present records exist, but answer quality and safe_for_agent_use remain human-owned review judgments."
    ]


def _boolean_counts(value: Any) -> dict[str, int]:
    counts = _count_mapping(value)
    return {
        "false": _safe_int(counts.get("false")),
        "true": _safe_int(counts.get("true")),
    }


def _count_mapping(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    return {
        _text(key): _safe_int(count)
        for key, count in value.items()
        if _text(key)
    }


def _format_counts(value: Any) -> str:
    counts = _count_mapping(value)
    if not counts:
        return "`none`"
    return ", ".join(f"`{key}: {counts[key]}`" for key in sorted(counts))


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    return 0


def _text(value: Any) -> str:
    return str(value or "").strip()
