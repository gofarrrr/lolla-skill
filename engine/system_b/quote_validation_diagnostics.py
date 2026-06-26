"""Deterministic diagnostics for quote-validation failures.

This module inspects archived extraction artifacts to classify why recorded
``reasoning_passages`` failed literal quote validation. It is intentionally
diagnostic-only: it does not change runtime matching behavior, call models, or
export raw transcript or fabricated-passage text.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .conversation_loader import _parse_turns
from .text_matching import find_substring_tolerant


QUOTE_VALIDATION_DIAGNOSTIC_RECORD_SCHEMA_VERSION = (
    "lolla.quote_validation_diagnostic_record.v0"
)
QUOTE_VALIDATION_FINDINGS_SCHEMA_VERSION = "lolla.quote_validation_findings.v0"

CLASSIFICATIONS = (
    "accepted_by_current_matcher",
    "whitespace_normalized_match",
    "unicode_punctuation_normalized_match",
    "linebreak_normalized_match",
    "high_token_overlap_near_match",
    "true_paraphrase_or_no_match",
    "empty_or_invalid_passage",
)

FORMAT_MATCH_CLASSIFICATIONS = {
    "whitespace_normalized_match",
    "unicode_punctuation_normalized_match",
    "linebreak_normalized_match",
}

_PUNCT_TRANSLATION = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
        "\u2032": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u201f": '"',
        "\u2033": '"',
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2015": "-",
        "\u2212": "-",
        "\u2026": "...",
    }
)
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


def build_quote_validation_diagnostic_record(
    run_dir: Path | str,
    *,
    archive_root: Path | str | None = None,
) -> dict[str, Any]:
    """Classify quote-validation failures for one archived run directory."""

    run_path = Path(run_dir)
    root = Path(archive_root).expanduser() if archive_root is not None else None
    case_id = _bounded_text(run_path.parent.name) or "unknown-case"
    run_id = _bounded_text(run_path.name) or "unknown-run"
    errors: list[str] = []

    conversation_path = run_path / "conversation.txt"
    extraction_path = run_path / "extraction.json"
    conversation_present = conversation_path.is_file()
    extraction_present = extraction_path.is_file()
    conversation_text = _read_text(conversation_path, errors, "conversation.txt")
    extraction = _read_json_object(extraction_path, errors, "extraction.json")
    extraction_payload = _mapping(extraction.get("extraction"))
    quote_validation = _mapping(extraction_payload.get("_quote_validation"))
    fabricated_passages = _list(quote_validation.get("fabricated_passages"))
    turns = _parse_turns(conversation_text) if conversation_text else ()

    passage_diagnostics = [
        _diagnose_passage(passage, conversation_text=conversation_text, turns=turns)
        for passage in fabricated_passages
    ]
    classification_counts = _classification_counts(passage_diagnostics)
    record_status = "valid"
    if errors or not conversation_present or not extraction_present:
        record_status = "invalid"

    return {
        "schema_version": QUOTE_VALIDATION_DIAGNOSTIC_RECORD_SCHEMA_VERSION,
        "case_id": case_id,
        "run_id": run_id,
        "archive_relpath": _archive_relpath(run_path, root, case_id, run_id),
        "record_status": record_status,
        "error_categories": _error_categories(errors),
        "quote_validation_present": bool(quote_validation),
        "fabricated_count_reported": _safe_int(quote_validation.get("fabricated")),
        "fabricated_passage_count_seen": len(fabricated_passages),
        "retry_attempted": bool(quote_validation.get("retry_attempted")),
        "retry_succeeded": bool(quote_validation.get("retry_succeeded")),
        "conversation_present": conversation_present,
        "extraction_present": extraction_present,
        "classification_counts": classification_counts,
        "passage_diagnostics": passage_diagnostics,
        "recommended_repair": _recommended_record_repair(
            classification_counts=classification_counts,
            record_status=record_status,
            retry_attempted=bool(quote_validation.get("retry_attempted")),
            retry_succeeded=bool(quote_validation.get("retry_succeeded")),
        ),
        "notes": _record_notes(
            quote_validation=quote_validation,
            fabricated_passage_count=len(fabricated_passages),
            errors=errors,
        ),
    }


def build_quote_validation_findings(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Aggregate quote-validation diagnostic records into a findings report."""

    sorted_records = sorted(records, key=_record_sort_key)
    classification_counts: Counter[str] = Counter()
    for record in sorted_records:
        classification_counts.update(_counter_from_mapping(record.get("classification_counts")))
    invalid_record_count = sum(
        1 for record in sorted_records if _text(record.get("record_status")) != "valid"
    )
    retry_attempted_count = sum(1 for record in sorted_records if record.get("retry_attempted"))
    retry_succeeded_count = sum(1 for record in sorted_records if record.get("retry_succeeded"))

    return {
        "schema_version": QUOTE_VALIDATION_FINDINGS_SCHEMA_VERSION,
        "source": {
            "local_only": True,
            "shareable_without_review": False,
            "raw_archives_read": True,
            "raw_transcript_included": False,
            "raw_failed_quote_text_included": False,
            "raw_memo_included": False,
            "raw_revised_answer_included": False,
            "raw_model_message_content_included": False,
            "provider_reasoning_details_included": False,
            "absolute_archive_paths_included": False,
            "model_calls": 0,
            "llm_judge_used": False,
        },
        "record_count": len(sorted_records),
        "valid_record_count": len(sorted_records) - invalid_record_count,
        "invalid_record_count": invalid_record_count,
        "passage_count": sum(
            _safe_int(record.get("fabricated_passage_count_seen"))
            for record in sorted_records
        ),
        "classification_counts": _counter_dict(classification_counts),
        "retry_attempted_count": retry_attempted_count,
        "retry_succeeded_count": retry_succeeded_count,
        "records": [dict(record) for record in sorted_records],
        "recommended_next_slice": _recommended_next_slice(
            classification_counts=classification_counts,
            record_count=len(sorted_records),
            invalid_record_count=invalid_record_count,
            retry_attempted_count=retry_attempted_count,
            retry_succeeded_count=retry_succeeded_count,
        ),
    }


def render_quote_validation_findings_markdown(findings: Mapping[str, Any]) -> str:
    """Render aggregate quote-validation findings as compact Markdown."""

    recommendation = _mapping(findings.get("recommended_next_slice"))
    lines = [
        "# Quote Validation Failure Findings",
        "",
        "## Summary",
        "",
        f"- Records inspected: `{_safe_int(findings.get('record_count'))}`",
        f"- Fabricated passages inspected: `{_safe_int(findings.get('passage_count'))}`",
        (
            f"- Valid/invalid records: `{_safe_int(findings.get('valid_record_count'))}` / "
            f"`{_safe_int(findings.get('invalid_record_count'))}`"
        ),
        (
            f"- Retry attempted/succeeded records: "
            f"`{_safe_int(findings.get('retry_attempted_count'))}` / "
            f"`{_safe_int(findings.get('retry_succeeded_count'))}`"
        ),
        "",
        "## Classification Counts",
        "",
        _format_count_map(_mapping(findings.get("classification_counts"))),
        "",
        "## Affected Records",
        "",
    ]
    lines.extend(_record_table(_list(findings.get("records"))))
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
            "- No runtime quote-validator behavior change.",
            "- No prompt change, model call, LLM judge, or answer-quality scoring.",
            "- No graph DB, embeddings, Observatory work, or control-plane changes.",
            "- No `conversation_understanding_ir.v0` implementation.",
            "- No raw transcript or fabricated-passage text in this report.",
            "",
        ]
    )
    return "\n".join(lines)


def render_quote_validation_findings_json(findings: Mapping[str, Any]) -> str:
    return json.dumps(findings, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _diagnose_passage(
    passage: Any,
    *,
    conversation_text: str,
    turns: Sequence[Any],
) -> dict[str, Any]:
    nearest = _nearest_turn(passage, turns) if isinstance(passage, str) else _empty_nearest()
    if not isinstance(passage, str) or not passage.strip():
        classification = "empty_or_invalid_passage"
        current_accepts = False
        diagnostic_accepts = False
    else:
        current_accepts = find_substring_tolerant(passage, conversation_text) is not None
        classification = _classify_passage(passage, conversation_text, nearest["token_overlap"])
        diagnostic_accepts = classification in {
            "whitespace_normalized_match",
            "unicode_punctuation_normalized_match",
            "linebreak_normalized_match",
            "high_token_overlap_near_match",
        }
    return {
        "passage_sha256": _sha256_uri(passage if isinstance(passage, str) else ""),
        "passage_length": len(passage) if isinstance(passage, str) else 0,
        "classification": classification,
        "current_matcher_accepts": current_accepts,
        "diagnostic_only_matcher_accepts": diagnostic_accepts,
        "nearest_turn_index": nearest["turn_index"],
        "nearest_turn_speaker": nearest["speaker"],
        "token_overlap": nearest["token_overlap"],
    }


def _classify_passage(
    passage: str,
    conversation_text: str,
    token_overlap: float,
) -> str:
    if find_substring_tolerant(passage, conversation_text) is not None:
        return "accepted_by_current_matcher"
    if _linebreak_normalized_contains(passage, conversation_text):
        return "linebreak_normalized_match"
    if _unicode_punctuation_normalized_contains(passage, conversation_text):
        return "unicode_punctuation_normalized_match"
    if _whitespace_normalized_contains(passage, conversation_text):
        return "whitespace_normalized_match"
    if token_overlap >= 0.90:
        return "high_token_overlap_near_match"
    return "true_paraphrase_or_no_match"


def _linebreak_normalized_contains(needle: str, haystack: str) -> bool:
    return _normalize_linebreaks(needle).casefold() in _normalize_linebreaks(haystack).casefold()


def _whitespace_normalized_contains(needle: str, haystack: str) -> bool:
    return _normalize_whitespace(needle).casefold() in _normalize_whitespace(haystack).casefold()


def _unicode_punctuation_normalized_contains(needle: str, haystack: str) -> bool:
    return (
        _normalize_unicode_punctuation(needle).casefold()
        in _normalize_unicode_punctuation(haystack).casefold()
    )


def _normalize_linebreaks(value: str) -> str:
    return re.sub(r"\s*\r?\n\s*", " ", value).strip()


def _normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def _normalize_unicode_punctuation(value: str) -> str:
    return unicodedata.normalize("NFKC", value).translate(_PUNCT_TRANSLATION).strip()


def _nearest_turn(passage: Any, turns: Sequence[Any]) -> dict[str, Any]:
    passage_tokens = _tokens(passage) if isinstance(passage, str) else set()
    if not passage_tokens or not turns:
        return _empty_nearest()
    candidates = []
    for turn in turns:
        turn_tokens = _tokens(getattr(turn, "text", ""))
        overlap = len(passage_tokens & turn_tokens) / len(passage_tokens)
        candidates.append(
            {
                "turn_index": getattr(turn, "turn_index", None),
                "speaker": getattr(turn, "speaker", None),
                "token_overlap": round(overlap, 3),
            }
        )
    return sorted(
        candidates,
        key=lambda item: (
            -float(item["token_overlap"]),
            0 if item["speaker"] == "assistant" else 1,
            _safe_int(item["turn_index"]),
        ),
    )[0]


def _empty_nearest() -> dict[str, Any]:
    return {"turn_index": None, "speaker": "", "token_overlap": 0.0}


def _tokens(value: str) -> set[str]:
    return {
        token.casefold()
        for token in _TOKEN_RE.findall(_normalize_unicode_punctuation(value))
    }


def _classification_counts(passage_diagnostics: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for item in passage_diagnostics:
        counter[_text(item.get("classification")) or "true_paraphrase_or_no_match"] += 1
    return {key: counter.get(key, 0) for key in CLASSIFICATIONS}


def _recommended_record_repair(
    *,
    classification_counts: Mapping[str, Any],
    record_status: str,
    retry_attempted: bool,
    retry_succeeded: bool,
) -> str:
    if record_status != "valid":
        return "needs_manual_review"
    counts = _counter_from_mapping(classification_counts)
    if not sum(counts.values()):
        return "legacy_only"
    dominant = _dominant_classification(counts)
    if dominant == "accepted_by_current_matcher":
        return "legacy_only"
    if dominant in FORMAT_MATCH_CLASSIFICATIONS:
        return "matcher_tolerance"
    if dominant == "true_paraphrase_or_no_match":
        return "retry_prompt" if retry_attempted and not retry_succeeded else "extraction_prompt"
    if dominant == "high_token_overlap_near_match":
        return "needs_manual_review"
    return "needs_manual_review"


def _recommended_next_slice(
    *,
    classification_counts: Counter[str],
    record_count: int,
    invalid_record_count: int,
    retry_attempted_count: int,
    retry_succeeded_count: int,
) -> dict[str, str]:
    total = sum(classification_counts.values())
    if invalid_record_count and invalid_record_count >= record_count:
        return {
            "slice": "needs_manual_archive_review",
            "reason": (
                f"All {record_count} inspected record(s) were "
                "missing or malformed, so archive condition must be separated before "
                "quote-validation repair."
            ),
        }
    if total <= 0:
        return {
            "slice": "legacy_only_no_runtime_change",
            "reason": "No fabricated passages were available to classify.",
        }
    accepted = classification_counts.get("accepted_by_current_matcher", 0)
    formatting = sum(classification_counts.get(key, 0) for key in FORMAT_MATCH_CLASSIFICATIONS)
    paraphrase = classification_counts.get("true_paraphrase_or_no_match", 0)
    near = classification_counts.get("high_token_overlap_near_match", 0)
    empty = classification_counts.get("empty_or_invalid_passage", 0)
    if accepted / total >= 0.5:
        return {
            "slice": "legacy_only_no_runtime_change",
            "reason": (
                f"Current matcher now accepts {accepted} of {total} old failure(s); "
                f"{_invalid_record_note(invalid_record_count, record_count)}"
                "run a modern smoke before changing runtime behavior."
            ),
        }
    if formatting / total >= 0.5 and formatting >= paraphrase:
        return {
            "slice": "matcher_tolerance_repair",
            "reason": (
                f"Formatting-only mismatches account for {formatting} of {total} "
                f"failure(s); {_invalid_record_note(invalid_record_count, record_count)}"
                "deterministic matcher tolerance is the narrowest "
                "candidate repair."
            ),
        }
    if paraphrase / total >= 0.5:
        if retry_attempted_count and retry_succeeded_count == 0:
            return {
                "slice": "retry_prompt_repair",
                "reason": (
                    f"True paraphrase/no-match accounts for {paraphrase} of {total} "
                    f"failure(s); {_invalid_record_note(invalid_record_count, record_count)}"
                    "retry did not fully recover the inspected records."
                ),
            }
        return {
            "slice": "extraction_prompt_repair",
            "reason": (
                f"True paraphrase/no-match accounts for {paraphrase} of {total} "
                f"failure(s); {_invalid_record_note(invalid_record_count, record_count)}"
                "the extractor is not consistently producing "
                "literal quotes."
            ),
        }
    return {
        "slice": "quote_validation_repair_plan",
        "reason": (
            f"Failures are mixed across current={accepted}, formatting={formatting}, "
            f"near={near}, paraphrase={paraphrase}, and empty={empty}; split the "
            f"next repair plan before changing runtime behavior. "
            f"{_invalid_record_note(invalid_record_count, record_count)}"
        ),
    }


def _invalid_record_note(invalid_record_count: int, record_count: int) -> str:
    if invalid_record_count <= 0:
        return ""
    return (
        f"{invalid_record_count} of {record_count} record(s) were missing or malformed "
        "and should be treated as archive-condition evidence; "
    )


def _record_notes(
    *,
    quote_validation: Mapping[str, Any],
    fabricated_passage_count: int,
    errors: Sequence[str],
) -> list[str]:
    notes: list[str] = []
    if errors:
        notes.append("archive_missing_or_malformed")
    if not quote_validation:
        notes.append("quote_validation_metadata_missing")
    reported = _safe_int(quote_validation.get("fabricated"))
    if reported != fabricated_passage_count:
        notes.append("fabricated_count_differs_from_passage_list")
    return sorted(set(notes))


def _read_text(path: Path, errors: list[str], artifact_name: str) -> str:
    if not path.exists():
        errors.append(f"{artifact_name} missing")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        errors.append(f"{artifact_name} unreadable")
        return ""


def _read_json_object(path: Path, errors: list[str], artifact_name: str) -> dict[str, Any]:
    if not path.exists():
        errors.append(f"{artifact_name} missing")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        errors.append(f"{artifact_name} invalid_json")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{artifact_name} non_object_json")
        return {}
    return payload


def _error_categories(errors: Sequence[str]) -> list[str]:
    categories = []
    for error in errors:
        if error.endswith(" missing"):
            categories.append("missing_artifact")
        elif error.endswith(" invalid_json"):
            categories.append("invalid_json_artifact")
        elif error.endswith(" non_object_json"):
            categories.append("non_object_json_artifact")
        elif error.endswith(" unreadable"):
            categories.append("unreadable_artifact")
        else:
            categories.append("archive_error")
    return sorted(set(categories))


def _archive_relpath(
    run_path: Path,
    root: Path | None,
    case_id: str,
    run_id: str,
) -> str:
    if root is not None:
        try:
            relpath = run_path.relative_to(root)
            if not relpath.is_absolute():
                return _bounded_text(str(relpath))
        except ValueError:
            pass
    return f"{case_id}/{run_id}"


def _record_sort_key(record: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        _text(record.get("case_id")),
        _text(record.get("run_id")),
        _text(record.get("archive_relpath")),
    )


def _record_table(records: Sequence[Any]) -> list[str]:
    if not records:
        return ["No records."]
    lines = [
        "| id | classifications | retry | repair |",
        "|---|---:|---:|---|",
    ]
    for item in records:
        record = _mapping(item)
        classifications = _format_count_map(_mapping(record.get("classification_counts")))
        retry = (
            f"{str(bool(record.get('retry_attempted'))).lower()}/"
            f"{str(bool(record.get('retry_succeeded'))).lower()}"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(_record_id(record)),
                    _md(classifications),
                    _md(retry),
                    _md(_text(record.get("recommended_repair")) or "unknown"),
                ]
            )
            + " |"
        )
    return lines


def _record_id(record: Mapping[str, Any]) -> str:
    return f"{_text(record.get('case_id'))}/{_text(record.get('run_id'))}"


def _dominant_classification(counts: Counter[str]) -> str:
    nonzero = [(key, counts.get(key, 0)) for key in CLASSIFICATIONS if counts.get(key, 0)]
    if not nonzero:
        return "true_paraphrase_or_no_match"
    return sorted(nonzero, key=lambda item: (-item[1], CLASSIFICATIONS.index(item[0])))[0][0]


def _counter_from_mapping(value: Any) -> Counter[str]:
    counter: Counter[str] = Counter()
    for key, count in _mapping(value).items():
        text = _text(key)
        if text:
            counter[text] += _safe_int(count)
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


def _format_count_map(value: Mapping[str, Any]) -> str:
    if not value:
        return "none"
    return ", ".join(f"`{_text(key)}`: `{_safe_int(count)}`" for key, count in value.items())


def _sha256_uri(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


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


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()
