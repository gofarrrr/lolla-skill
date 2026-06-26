#!/usr/bin/env python3
"""Analyze a PR21 extraction-adequacy corpus export.

The analyzer intentionally reads only the compact PR21 JSONL records and
manifest. It does not inspect archived run folders, transcript text, memo text,
revised answers, model messages, provider details, or control arguments.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


FINDINGS_SCHEMA_VERSION = "lolla.extraction_adequacy_findings.v0"

KNOWN_EXTRACTION_FIELDS = {
    "decision_situation",
    "dropped_threads",
    "live_constraints",
    "original_framing",
    "reasoning_passages",
    "synthesized_position",
}

SPECIALIST_TO_SLICE = {
    "live_constraints_extraction": "live_constraints_span_grounding",
    "dropped_threads_extraction": "dropped_threads_span_grounding",
    "stance_extraction": "stance_extraction_grounding",
}
SPECIALIST_PRIORITY = {
    "live_constraints_extraction": 0,
    "dropped_threads_extraction": 1,
    "stance_extraction": 2,
}

NEXT_SLICES = {
    "turn_ref_repair_or_validation",
    "quote_validation_repair",
    "stance_extraction_grounding",
    "live_constraints_span_grounding",
    "dropped_threads_span_grounding",
    "legacy_backfill_tooling",
    "no_extraction_change_yet_run_new_smoke",
}


class InputError(ValueError):
    """Deterministic, sanitized user-facing input error."""


def load_corpus_jsonl(path: Path | str) -> list[dict[str, Any]]:
    corpus_path = Path(path)
    try:
        lines = corpus_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise InputError(f"corpus could not be read:{type(exc).__name__}") from exc

    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InputError(f"corpus line {line_number} is not valid JSON") from exc
        if not isinstance(payload, dict):
            raise InputError(f"corpus line {line_number} is not a JSON object")
        records.append(payload)
    return records


def load_manifest(path: Path | str) -> dict[str, Any]:
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


def build_findings(
    records: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    *,
    corpus_path: Path | str | None = None,
    manifest_path: Path | str | None = None,
) -> dict[str, Any]:
    sorted_records = sorted(records, key=_record_sort_key)
    critical_records = [
        _record_drilldown(record)
        for record in sorted_records
        if _text(record.get("adequacy_status")) == "critical"
    ]
    warning_records = [
        _record_drilldown(record)
        for record in sorted_records
        if _text(record.get("adequacy_status")) == "warn"
    ]
    invalid_turn_ref_records = [
        _record_drilldown(record)
        for record in sorted_records
        if _safe_int(record.get("invalid_turn_ref_count")) > 0
    ]
    quote_fabrication_records = [
        _record_drilldown(record)
        for record in sorted_records
        if _safe_int(record.get("quote_fabrication_count")) > 0
    ]

    warning_category_counts = Counter()
    critical_category_counts = Counter()
    for record in sorted_records:
        status = _text(record.get("adequacy_status"))
        if status == "warn":
            warning_category_counts.update(_status_categories(record))
        elif status == "critical":
            critical_category_counts.update(_status_categories(record))

    specialist_counts = _counter_from_mapping(
        _mapping(manifest.get("specialist_opportunity_counts"))
    )
    most_actionable_specialist = _most_actionable_specialist(specialist_counts)
    quote_patterns = _count_pattern(
        records=quote_fabrication_records,
        count_key="quote_fabrication_count",
    )
    invalid_turn_patterns = _count_pattern(
        records=invalid_turn_ref_records,
        count_key="invalid_turn_ref_count",
    )
    warning_distribution = _record_distribution(warning_records)

    findings: dict[str, Any] = {
        "schema_version": FINDINGS_SCHEMA_VERSION,
        "source": {
            "corpus": str(corpus_path) if corpus_path is not None else "",
            "manifest": str(manifest_path) if manifest_path is not None else "",
            "local_only": True,
            "shareable_without_review": False,
            "raw_archives_read": False,
            "absolute_archive_paths_included": False,
            "raw_transcript_included": False,
            "raw_memo_included": False,
            "raw_revised_answer_included": False,
            "raw_model_message_content_included": False,
            "provider_reasoning_details_included": False,
            "control_argument_values_included": False,
            "model_calls": 0,
            "llm_judge_used": False,
        },
        "corpus_summary": _corpus_summary(sorted_records, manifest),
        "critical_records": critical_records,
        "warning_records": warning_records,
        "invalid_turn_ref_patterns": {
            "total": _manifest_or_sum(
                manifest,
                sorted_records,
                "invalid_turn_ref_total",
                "invalid_turn_ref_count",
            ),
            "record_count": len(invalid_turn_ref_records),
            "records": invalid_turn_ref_records,
            "distribution": invalid_turn_patterns,
        },
        "quote_fabrication_patterns": {
            "total": _manifest_or_sum(
                manifest,
                sorted_records,
                "quote_fabrication_total",
                "quote_fabrication_count",
            ),
            "record_count": len(quote_fabrication_records),
            "records": quote_fabrication_records,
            "distribution": quote_patterns,
        },
        "legacy_metadata_limits": _legacy_metadata_limits(sorted_records, manifest),
        "warning_cause_counts": _counter_dict(warning_category_counts),
        "critical_cause_counts": _counter_dict(critical_category_counts),
        "warning_distribution": warning_distribution,
        "specialist_extractor_opportunities": {
            "counts": _counter_dict(specialist_counts),
            "most_actionable_diagnostic": most_actionable_specialist,
            "caution": (
                "Specialist opportunity counts are diagnostic coverage signals, "
                "not proof that a specialist should run in production."
            ),
        },
    }
    findings["recommended_next_slice"] = _recommended_next_slice(findings)
    return findings


def render_markdown(findings: Mapping[str, Any]) -> str:
    summary = _mapping(findings.get("corpus_summary"))
    legacy = _mapping(findings.get("legacy_metadata_limits"))
    invalid_patterns = _mapping(findings.get("invalid_turn_ref_patterns"))
    quote_patterns = _mapping(findings.get("quote_fabrication_patterns"))
    specialist = _mapping(findings.get("specialist_extractor_opportunities"))
    recommendation = _mapping(findings.get("recommended_next_slice"))

    lines = [
        "# Extraction Adequacy Findings",
        "",
        "## Corpus Summary",
        "",
        f"- Records: `{_safe_int(summary.get('record_count'))}`",
        (
            f"- Valid/invalid: `{_safe_int(summary.get('valid_record_count'))}` / "
            f"`{_safe_int(summary.get('invalid_record_count'))}`"
        ),
        f"- Adequacy statuses: {_format_count_map(summary.get('adequacy_status_counts'))}",
        (
            "- Capture adequacy statuses: "
            f"{_format_count_map(summary.get('capture_adequacy_status_counts'))}"
        ),
        (
            f"- Reports available/missing/built in memory: "
            f"`{_safe_int(summary.get('report_available_count'))}` / "
            f"`{_safe_int(summary.get('report_missing_count'))}` / "
            f"`{_safe_int(summary.get('report_built_in_memory_count'))}`"
        ),
        (
            f"- Context/IR available: "
            f"`{_safe_int(summary.get('conversation_context_available_count'))}` / "
            f"`{_safe_int(summary.get('conversation_ir_available_count'))}`"
        ),
        (
            f"- Non-good records: `{len(_list(findings.get('critical_records'))) + len(_list(findings.get('warning_records')))}` "
            f"(`{len(_list(findings.get('critical_records')))}` critical, "
            f"`{len(_list(findings.get('warning_records')))}` warning)"
        ),
        "",
        "## Critical Records",
        "",
    ]
    lines.extend(_record_table(_list(findings.get("critical_records"))))
    lines.extend(
        [
            "",
            "## Warning Records",
            "",
        ]
    )
    lines.extend(_record_table(_list(findings.get("warning_records"))))
    lines.extend(
        [
            "",
            "## Invalid Turn Ref Patterns",
            "",
            f"- Total invalid turn refs: `{_safe_int(invalid_patterns.get('total'))}`",
            f"- Records affected: `{_safe_int(invalid_patterns.get('record_count'))}`",
            (
                "- Concentration: "
                f"`{_text(_mapping(invalid_patterns.get('distribution')).get('concentration')) or 'none'}`"
            ),
            "",
        ]
    )
    lines.extend(_record_table(_list(invalid_patterns.get("records"))))
    lines.extend(
        [
            "",
            "## Quote Fabrication Patterns",
            "",
            f"- Total quote fabrication count: `{_safe_int(quote_patterns.get('total'))}`",
            f"- Records affected: `{_safe_int(quote_patterns.get('record_count'))}`",
            (
                "- Concentration: "
                f"`{_text(_mapping(quote_patterns.get('distribution')).get('concentration')) or 'none'}`"
            ),
            (
                "- Warning distribution: "
                f"`{_text(_mapping(findings.get('warning_distribution')).get('concentration')) or 'none'}`"
            ),
            "",
        ]
    )
    lines.extend(_record_table(_list(quote_patterns.get("records"))))
    lines.extend(
        [
            "",
            "## Legacy Metadata Limits",
            "",
            (
                f"- Missing extraction adequacy report artifacts: "
                f"`{_safe_int(legacy.get('report_missing_count'))}`"
            ),
            (
                f"- Built in memory during export: "
                f"`{_safe_int(legacy.get('report_built_in_memory_count'))}`"
            ),
            (
                f"- Unknown capture adequacy metadata: "
                f"`{_safe_int(legacy.get('capture_adequacy_unknown_count'))}`"
            ),
            (
                f"- Unknown capture strategy metadata: "
                f"`{_safe_int(legacy.get('capture_strategy_unknown_count'))}`"
            ),
            (
                "- Interpretation: legacy metadata limits are broad corpus limits; "
                "they are not, by themselves, answer-quality or extraction-correctness failures."
            ),
            "",
            "## Specialist Extractor Opportunities",
            "",
            f"- Counts: {_format_count_map(_mapping(specialist.get('counts')))}",
        ]
    )
    most_actionable = _mapping(specialist.get("most_actionable_diagnostic"))
    if most_actionable:
        lines.extend(
            [
                (
                    f"- Largest specialist coverage signal: "
                    f"`{_text(most_actionable.get('candidate_slice'))}` from "
                    f"`{_text(most_actionable.get('specialist'))}` "
                    f"(`{_safe_int(most_actionable.get('record_count'))}` records)"
                ),
                (
                    "- Caveat: this is a coverage signal, not a production-routing "
                    "decision."
                ),
            ]
        )
    else:
        lines.append("- Most actionable diagnostic opportunity: none")
    lines.extend(
        [
            "",
            "## Recommended Next Slice",
            "",
            f"- Recommendation: `{_text(recommendation.get('slice'))}`",
            f"- Reason: {_text(recommendation.get('reason'))}",
            "",
            "## Non-Goals",
            "",
            "- No runtime behavior change.",
            "- No model calls, LLM judge, answer-quality scoring, or prompt changes.",
            "- No graph DB, embeddings, Observatory work, or control-plane changes.",
            "- No `conversation_understanding_ir.v0` implementation in this slice.",
            "- No automatic human-review labels.",
            "",
        ]
    )
    return "\n".join(lines)


def render_json(findings: Mapping[str, Any]) -> str:
    return json.dumps(findings, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_text(path: Path | str, payload: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic, privacy-bounded findings report from a "
            "PR21 extraction-adequacy corpus JSONL and manifest."
        )
    )
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path, help="Markdown findings path.")
    parser.add_argument("--json-out", required=True, type=Path, help="JSON findings path.")
    args = parser.parse_args(argv)

    try:
        records = load_corpus_jsonl(args.corpus)
        manifest = load_manifest(args.manifest)
        findings = build_findings(
            records,
            manifest,
            corpus_path=args.corpus,
            manifest_path=args.manifest,
        )
        write_text(args.out, render_markdown(findings))
        write_text(args.json_out, render_json(findings))
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def _record_drilldown(record: Mapping[str, Any]) -> dict[str, Any]:
    identity = _record_identity(record)
    return {
        **identity,
        "record_status": _text(record.get("record_status")) or "unknown",
        "adequacy_status": _text(record.get("adequacy_status")) or "unknown",
        "recommended_review_bucket": _text(record.get("recommended_review_bucket"))
        or "unknown",
        "invalid_turn_ref_count": _safe_int(record.get("invalid_turn_ref_count")),
        "missing_turn_ref_count": _safe_int(record.get("missing_turn_ref_count")),
        "speaker_mismatch_count": _safe_int(record.get("speaker_mismatch_count")),
        "quote_fabrication_count": _safe_int(record.get("quote_fabrication_count")),
        "omitted_turn_count": _safe_int(record.get("omitted_turn_count")),
        "conversation_context_available": bool(
            record.get("conversation_context_available")
        ),
        "conversation_ir_available": bool(record.get("conversation_ir_available")),
        "status_causes": _status_causes(record),
        "diagnostic_flags": _diagnostic_flags(record),
        "error_categories": _error_categories(record.get("record_errors")),
        "fields_only_turn_ref_grounded": _safe_field_names(
            record.get("fields_only_turn_ref_grounded")
        ),
        "fields_with_no_source_grounding": _safe_field_names(
            record.get("fields_with_no_source_grounding")
        ),
    }


def _record_identity(record: Mapping[str, Any]) -> dict[str, str | bool]:
    case_id = _bounded_text(record.get("case_id")) or "unknown-case"
    run_id = _bounded_text(record.get("run_id")) or "unknown-run"
    archive_path_present = bool(_text(record.get("archive_path")))
    archive_relpath = _bounded_text(record.get("archive_relpath")) or f"{case_id}/{run_id}"
    return {
        "id": f"{case_id}/{run_id}",
        "case_id": case_id,
        "run_id": run_id,
        "archive_relpath": archive_relpath,
        "archive_path_present": archive_path_present,
    }


def _corpus_summary(
    records: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "record_count": _safe_int(manifest.get("record_count"), len(records)),
        "valid_record_count": _safe_int(
            manifest.get("valid_record_count"),
            sum(1 for record in records if _text(record.get("record_status")) == "valid"),
        ),
        "invalid_record_count": _safe_int(
            manifest.get("invalid_record_count"),
            sum(1 for record in records if _text(record.get("record_status")) == "invalid"),
        ),
        "adequacy_status_counts": _counter_dict(
            _counter_from_mapping(
                _mapping(manifest.get("adequacy_status_counts"))
                or _count_records(records, "adequacy_status")
            )
        ),
        "capture_adequacy_status_counts": _counter_dict(
            _counter_from_mapping(
                _mapping(manifest.get("capture_adequacy_status_counts"))
                or _count_records(records, "capture_adequacy_status")
            )
        ),
        "capture_strategy_counts": _counter_dict(
            _counter_from_mapping(
                _mapping(manifest.get("capture_strategy_counts"))
                or _count_records(records, "capture_strategy")
            )
        ),
        "report_available_count": _safe_int(manifest.get("report_available_count")),
        "report_missing_count": _safe_int(manifest.get("report_missing_count")),
        "report_built_in_memory_count": _safe_int(
            manifest.get("report_built_in_memory_count")
        ),
        "invalid_turn_ref_total": _manifest_or_sum(
            manifest,
            records,
            "invalid_turn_ref_total",
            "invalid_turn_ref_count",
        ),
        "missing_turn_ref_total": _manifest_or_sum(
            manifest,
            records,
            "missing_turn_ref_total",
            "missing_turn_ref_count",
        ),
        "speaker_mismatch_total": _manifest_or_sum(
            manifest,
            records,
            "speaker_mismatch_total",
            "speaker_mismatch_count",
        ),
        "quote_fabrication_total": _manifest_or_sum(
            manifest,
            records,
            "quote_fabrication_total",
            "quote_fabrication_count",
        ),
        "omitted_turn_total": _manifest_or_sum(
            manifest,
            records,
            "omitted_turn_total",
            "omitted_turn_count",
        ),
        "conversation_context_available_count": _safe_int(
            manifest.get("conversation_context_available_count"),
            sum(1 for record in records if record.get("conversation_context_available")),
        ),
        "conversation_ir_available_count": _safe_int(
            manifest.get("conversation_ir_available_count"),
            sum(1 for record in records if record.get("conversation_ir_available")),
        ),
        "recommended_review_buckets": _counter_dict(
            _counter_from_mapping(
                _mapping(manifest.get("recommended_review_buckets"))
                or _count_records(records, "recommended_review_bucket")
            )
        ),
    }


def _legacy_metadata_limits(
    records: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "report_available_count": _safe_int(manifest.get("report_available_count")),
        "report_missing_count": _safe_int(manifest.get("report_missing_count")),
        "report_built_in_memory_count": _safe_int(
            manifest.get("report_built_in_memory_count")
        ),
        "capture_adequacy_unknown_count": sum(
            1
            for record in records
            if (_text(record.get("capture_adequacy_status")) or "unknown") == "unknown"
        ),
        "capture_strategy_unknown_count": sum(
            1
            for record in records
            if (_text(record.get("capture_strategy")) or "unknown") == "unknown"
        ),
        "all_reports_built_in_memory": bool(records)
        and _safe_int(manifest.get("report_built_in_memory_count")) == len(records),
    }


def _status_causes(record: Mapping[str, Any]) -> list[str]:
    causes: list[str] = []
    if _text(record.get("record_status")) == "invalid":
        causes.append("invalid_record")
    if not record.get("conversation_context_available"):
        causes.append("conversation_context_unavailable")
    if not record.get("conversation_ir_available"):
        causes.append("conversation_ir_unavailable")
    if _safe_int(record.get("invalid_turn_ref_count")) > 0:
        causes.append("invalid_turn_refs")
    if _safe_int(record.get("missing_turn_ref_count")) > 0:
        causes.append("missing_turn_refs")
    if _safe_int(record.get("speaker_mismatch_count")) > 0:
        causes.append("speaker_mismatch")
    if _safe_int(record.get("quote_fabrication_count")) > 0:
        causes.append("quote_fabrication")
    if _safe_int(record.get("omitted_turn_count")) > 0:
        causes.append("omitted_turns")
    capture_status = _text(record.get("capture_adequacy_status"))
    if capture_status in {"critical", "warn"}:
        causes.append(f"capture_adequacy_{capture_status}")
    if not causes and _text(record.get("adequacy_status")) in {"critical", "warn"}:
        if _safe_field_names(record.get("fields_with_no_source_grounding")):
            causes.append("no_source_grounding")
        elif _safe_field_names(record.get("fields_only_turn_ref_grounded")):
            causes.append("turn_ref_only_grounding")
        elif _text(record.get("capture_adequacy_status")) == "unknown":
            causes.append("legacy_capture_metadata_unknown")
        else:
            causes.append("unexplained_status")
    return sorted(set(causes))


def _diagnostic_flags(record: Mapping[str, Any]) -> list[str]:
    flags: list[str] = []
    if record.get("report_built_in_memory") and not record.get("report_available"):
        flags.append("legacy_report_built_in_memory")
    if (_text(record.get("capture_adequacy_status")) or "unknown") == "unknown":
        flags.append("legacy_capture_adequacy_unknown")
    if (_text(record.get("capture_strategy")) or "unknown") == "unknown":
        flags.append("legacy_capture_strategy_unknown")
    if _safe_field_names(record.get("fields_only_turn_ref_grounded")):
        flags.append("fields_only_turn_ref_grounded")
    if _safe_field_names(record.get("fields_with_no_source_grounding")):
        flags.append("fields_with_no_source_grounding")
    return sorted(set(flags))


def _status_categories(record: Mapping[str, Any]) -> list[str]:
    categories: list[str] = []
    if _text(record.get("record_status")) == "invalid":
        categories.append("malformed_archive")
    if (
        _safe_int(record.get("invalid_turn_ref_count")) > 0
        or _safe_int(record.get("missing_turn_ref_count")) > 0
        or _safe_int(record.get("speaker_mismatch_count")) > 0
    ):
        categories.append("turn_refs")
    if _safe_int(record.get("quote_fabrication_count")) > 0:
        categories.append("quote_validation")
    if (
        not record.get("conversation_context_available")
        or not record.get("conversation_ir_available")
    ):
        categories.append("context_ir")
    if (
        _safe_int(record.get("omitted_turn_count")) > 0
        or _text(record.get("capture_adequacy_status")) in {"critical", "warn"}
    ):
        categories.append("capture_or_omission")
    if not categories:
        if (
            _text(record.get("capture_adequacy_status")) == "unknown"
            or record.get("report_built_in_memory")
        ):
            categories.append("legacy_metadata")
        elif (
            _safe_field_names(record.get("fields_only_turn_ref_grounded"))
            or _safe_field_names(record.get("fields_with_no_source_grounding"))
        ):
            categories.append("provenance_gaps")
        else:
            categories.append("unclassified")
    return sorted(set(categories))


def _count_pattern(
    *,
    records: Sequence[Mapping[str, Any]],
    count_key: str,
) -> dict[str, Any]:
    counts = [_safe_int(record.get(count_key)) for record in records]
    total = sum(counts)
    if total <= 0:
        return {
            "concentration": "none",
            "max_record_count": 0,
            "max_record_ids": [],
        }
    max_count = max(counts)
    max_ids = [
        _text(record.get("id"))
        for record in records
        if _safe_int(record.get(count_key)) == max_count
    ]
    ratio = max_count / total
    if len(records) == 1 or ratio >= 0.5:
        concentration = "concentrated"
    elif len(records) >= 3 and ratio <= 0.4:
        concentration = "spread"
    else:
        concentration = "mixed"
    return {
        "concentration": concentration,
        "max_record_count": max_count,
        "max_record_ids": sorted(max_ids),
    }


def _record_distribution(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    case_counts = Counter(_text(record.get("case_id")) for record in records)
    case_counts.pop("", None)
    if not records:
        concentration = "none"
    elif len(case_counts) <= 1:
        concentration = "concentrated"
    else:
        max_case_count = max(case_counts.values())
        concentration = "concentrated" if max_case_count / len(records) >= 0.5 else "spread"
    return {
        "record_count": len(records),
        "case_count": len(case_counts),
        "case_counts": _counter_dict(case_counts),
        "concentration": concentration,
    }


def _most_actionable_specialist(
    counts: Counter[str],
) -> dict[str, Any] | None:
    candidates = [
        (key, count)
        for key, count in counts.items()
        if key in SPECIALIST_TO_SLICE and count > 0
    ]
    if not candidates:
        return None
    key, count = sorted(
        candidates,
        key=lambda item: (-item[1], SPECIALIST_PRIORITY.get(item[0], 99), item[0]),
    )[0]
    return {
        "specialist": key,
        "candidate_slice": SPECIALIST_TO_SLICE[key],
        "record_count": count,
    }


def _recommended_next_slice(findings: Mapping[str, Any]) -> dict[str, str]:
    critical_records = _list(findings.get("critical_records"))
    warning_records = _list(findings.get("warning_records"))
    quote_patterns = _mapping(findings.get("quote_fabrication_patterns"))
    invalid_patterns = _mapping(findings.get("invalid_turn_ref_patterns"))
    legacy = _mapping(findings.get("legacy_metadata_limits"))
    specialist = _mapping(findings.get("specialist_extractor_opportunities"))
    quote_record_count = _safe_int(quote_patterns.get("record_count"))
    quote_total = _safe_int(quote_patterns.get("total"))
    invalid_record_count = _safe_int(invalid_patterns.get("record_count"))
    invalid_total = _safe_int(invalid_patterns.get("total"))
    non_good_count = len(critical_records) + len(warning_records)

    if quote_record_count and quote_record_count >= invalid_record_count:
        return {
            "slice": "quote_validation_repair",
            "reason": (
                f"Quote fabrication appears in {quote_record_count} non-good "
                f"record(s) with {quote_total} total fabricated quote finding(s), "
                f"while invalid turn refs affect {invalid_record_count} record(s)."
            ),
        }
    if invalid_record_count:
        return {
            "slice": "turn_ref_repair_or_validation",
            "reason": (
                f"Invalid turn refs affect {invalid_record_count} record(s) "
                f"with {invalid_total} total invalid reference(s), including "
                "critical extraction failures."
            ),
        }
    if non_good_count == 0 and legacy.get("all_reports_built_in_memory"):
        return {
            "slice": "no_extraction_change_yet_run_new_smoke",
            "reason": (
                "The corpus has no non-good records, but the archive snapshot is "
                "legacy-only; run a new smoke with modern archived reports before "
                "changing extraction."
            ),
        }
    if legacy.get("all_reports_built_in_memory"):
        return {
            "slice": "legacy_backfill_tooling",
            "reason": (
                "Every report was built in memory from older archives, so a "
                "backfill/readiness slice would improve future corpus comparisons."
            ),
        }
    most_actionable = _mapping(specialist.get("most_actionable_diagnostic"))
    candidate = _text(most_actionable.get("candidate_slice"))
    if candidate in NEXT_SLICES:
        return {
            "slice": candidate,
            "reason": (
                f"The largest diagnostic specialist opportunity is {candidate}, "
                "and no stronger turn-ref or quote-validation failure pattern was found."
            ),
        }
    return {
        "slice": "no_extraction_change_yet_run_new_smoke",
        "reason": "No narrow extraction repair is justified by this corpus drilldown.",
    }


def _record_table(records: Sequence[Any]) -> list[str]:
    if not records:
        return ["No records."]
    lines = [
        "| id | path | causes | invalid refs | quote fab | context | IR |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for item in records:
        record = _mapping(item)
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(_text(record.get("id"))),
                    _md(_text(record.get("archive_relpath"))),
                    _md(", ".join(_strings(record.get("status_causes"))) or "none"),
                    str(_safe_int(record.get("invalid_turn_ref_count"))),
                    str(_safe_int(record.get("quote_fabrication_count"))),
                    _md(str(bool(record.get("conversation_context_available"))).lower()),
                    _md(str(bool(record.get("conversation_ir_available"))).lower()),
                ]
            )
            + " |"
        )
    return lines


def _record_sort_key(record: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        _text(record.get("case_id")),
        _text(record.get("run_id")),
        _text(record.get("archive_relpath")) or _text(record.get("archive_path")),
    )


def _manifest_or_sum(
    manifest: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    manifest_key: str,
    record_key: str,
) -> int:
    if manifest_key in manifest:
        return _safe_int(manifest.get(manifest_key))
    return sum(_safe_int(record.get(record_key)) for record in records)


def _counter_from_mapping(value: Mapping[str, Any]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for key, count in value.items():
        text = _text(key)
        if text:
            counter[text] += _safe_int(count)
    return counter


def _count_records(records: Sequence[Mapping[str, Any]], key: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for record in records:
        counter[_text(record.get(key)) or "unknown"] += 1
    return counter


def _counter_dict(counter: Counter[str] | Mapping[str, Any]) -> dict[str, int]:
    if not isinstance(counter, Counter):
        counter = _counter_from_mapping(counter)
    return {
        key: count
        for key, count in sorted(
            ((key, count) for key, count in counter.items() if key),
            key=lambda item: (-item[1], item[0]),
        )
    }


def _error_categories(value: Any) -> list[str]:
    categories: list[str] = []
    for item in _strings(value):
        if " is not valid JSON" in item:
            categories.append("invalid_json_artifact")
        elif " is not a JSON object" in item:
            categories.append("non_object_json_artifact")
        elif item == "no recognized Lolla run artifacts found":
            categories.append("no_recognized_artifacts")
        elif item.startswith("extraction adequacy report build failed:"):
            categories.append("report_build_failed")
        else:
            categories.append("record_error")
    return sorted(set(categories))


def _safe_field_names(value: Any) -> list[str]:
    return sorted(
        {
            item
            for item in _strings(value)
            if item in KNOWN_EXTRACTION_FIELDS
        }
    )


def _format_count_map(value: Any) -> str:
    payload = _mapping(value)
    if not payload:
        return "none"
    return ", ".join(f"`{_text(key)}`: `{_safe_int(count)}`" for key, count in payload.items())


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [_bounded_text(item) for item in value if _bounded_text(item)]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bounded_text(value: Any, *, limit: int = 240) -> str:
    text = _text(value).replace("\n", " ").replace("\r", " ").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 12].rstrip() + "...[truncated]"


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


if __name__ == "__main__":
    raise SystemExit(main())
