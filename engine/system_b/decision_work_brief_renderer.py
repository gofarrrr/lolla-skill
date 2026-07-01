"""Markdown renderer for Decision Work Brief artifacts.

This module renders an existing ``lolla.decision_work_brief.v0`` JSON object
into simple Markdown. It does not run Lolla, call models, mutate archives, read
raw/private content, judge answer quality, or infer missing semantic content.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any


DECISION_WORK_BRIEF_SCHEMA_VERSION = "lolla.decision_work_brief.v0"
DECISION_WORK_BRIEF_DRAFT_PILOT_SCHEMA_VERSION = (
    "lolla.decision_work_brief_draft_pilot.v0"
)
DECISION_WORK_BRIEF_SECOND_TINY_CASE_SCHEMA_VERSION = (
    "lolla.decision_work_brief_second_tiny_case_pilot.v0"
)
DECISION_WORK_BRIEF_THIRD_DIVERSITY_CASE_SCHEMA_VERSION = (
    "lolla.decision_work_brief_third_diversity_case_pilot.v0"
)

SECTION_ORDER = (
    "decision",
    "starting_direction",
    "what_lolla_pressed_on",
    "what_changed",
    "what_this_means_for_action",
    "what_still_might_be_wrong",
    "what_was_not_proven",
    "evidence_receipt",
)
SECTION_LABELS = {
    "decision": "the decision",
    "starting_direction": "the likely starting point",
    "what_lolla_pressed_on": "what Lolla pressed on",
    "what_changed": "what changed",
    "what_this_means_for_action": "what this means for action",
    "what_still_might_be_wrong": "what still might be wrong",
    "what_was_not_proven": "what this does not prove",
    "evidence_receipt": "the backing evidence",
}
STATUS_REQUIRING_PLAIN_MISSINGNESS = {
    "not_supplied",
    "unclear",
    "requires_human_review",
    "requires_llm_interpretation",
}
CUSTODY_FLAG_ORDER = (
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "model_calls",
    "raw_private_content_included",
    "provider_text_included",
    "raw_transcript_included",
    "raw_revised_answer_included",
    "raw_memo_included",
    "private_reasoning_included",
    "local_absolute_paths_included",
    "secrets_included",
    "llm_judge_used",
    "automatic_labels_created",
)
PLAIN_LABELS = {
    "candidate_starting_direction": "Likely starting point",
    "pressure_read": "Pressure point",
    "pressed_dimensions": "What was pressed",
    "change_read": "What changed",
    "specific_changes": "Specific changes",
    "candidate_next_actions": "Possible next actions",
    "missingness_and_uncertainty": "Missing or uncertain",
    "possible_overcorrection": "Possible overcorrection",
    "possible_overcorrection_or_noise": "Possible overcorrection or noise",
    "not_proven": "Not proven",
    "receipt_story": "Backing receipt",
    "available_evidence": "Available evidence",
    "withheld_or_redacted": "Unavailable or redacted",
}
UNLABELED_VALUE_KEYS = {
    "decision_story_read",
    "action_consequence",
}
MAIN_BODY_SKIP_KEYS = {
    "why_medium_uncertainty",
    "why_high_uncertainty",
    "why_low_uncertainty",
    "why_unclear",
}


class DecisionWorkBriefRendererInputError(ValueError):
    """Sanitized renderer input error."""


def load_json_object(path: Path | str) -> dict[str, Any]:
    """Load a JSON object from a path with sanitized errors."""

    input_path = Path(path).expanduser()
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DecisionWorkBriefRendererInputError("input JSON file was not found") from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkBriefRendererInputError("input JSON file was malformed") from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkBriefRendererInputError("input JSON file was not valid UTF-8") from exc
    except OSError as exc:
        raise DecisionWorkBriefRendererInputError(
            f"input JSON file could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkBriefRendererInputError("input JSON root was not an object")
    return payload


def extract_brief_from_pilot_review(
    *,
    pilot_review: Mapping[str, Any],
    brief_index: int = 0,
) -> dict[str, Any]:
    """Extract an embedded Decision Work Brief from a checked-in pilot review."""

    schema_version = pilot_review.get("schema_version")
    if schema_version == DECISION_WORK_BRIEF_DRAFT_PILOT_SCHEMA_VERSION:
        draft_briefs = pilot_review.get("draft_briefs")
        if not isinstance(draft_briefs, list):
            raise DecisionWorkBriefRendererInputError(
                "pilot review draft_briefs was not a list"
            )
        if brief_index < 0 or brief_index >= len(draft_briefs):
            raise DecisionWorkBriefRendererInputError("brief index was out of range")
        draft = draft_briefs[brief_index]
    elif schema_version == DECISION_WORK_BRIEF_SECOND_TINY_CASE_SCHEMA_VERSION:
        if brief_index != 0:
            raise DecisionWorkBriefRendererInputError("brief index was out of range")
        draft = pilot_review.get("second_case_brief")
    elif schema_version == DECISION_WORK_BRIEF_THIRD_DIVERSITY_CASE_SCHEMA_VERSION:
        if brief_index != 0:
            raise DecisionWorkBriefRendererInputError("brief index was out of range")
        draft = pilot_review.get("third_case_brief")
    else:
        raise DecisionWorkBriefRendererInputError("pilot review schema version was unsupported")
    if not isinstance(draft, Mapping):
        raise DecisionWorkBriefRendererInputError("pilot review draft entry was malformed")
    brief = draft.get("brief")
    if not isinstance(brief, dict):
        raise DecisionWorkBriefRendererInputError("pilot review draft did not embed a brief")
    validate_decision_work_brief(brief)
    return brief


def validate_decision_work_brief(brief: Mapping[str, Any]) -> None:
    """Validate the renderer's required subset of the PR114 brief contract."""

    if brief.get("schema_version") != DECISION_WORK_BRIEF_SCHEMA_VERSION:
        raise DecisionWorkBriefRendererInputError("brief schema version was unsupported")
    sections = brief.get("sections")
    if not isinstance(sections, Mapping):
        raise DecisionWorkBriefRendererInputError("brief sections were missing")
    missing = [section for section in SECTION_ORDER if section not in sections]
    if missing:
        raise DecisionWorkBriefRendererInputError("brief required sections were missing")
    for section_id in SECTION_ORDER:
        if not isinstance(sections.get(section_id), Mapping):
            raise DecisionWorkBriefRendererInputError("brief section was malformed")


def render_decision_work_brief_markdown(*, brief: Mapping[str, Any]) -> str:
    """Render an existing Decision Work Brief JSON object as Markdown."""

    validate_decision_work_brief(brief)
    metadata = _mapping(brief.get("brief_metadata"))
    sections = _mapping(brief.get("sections"))

    lines = [
        "# Decision Work Brief",
        "",
        "This is a provisional, non-human-validated Decision Work Brief. It explains what the audit artifacts suggest changed for the decision. It is not proof that the final answer is correct.",
        "",
        f"Case: `{_text(metadata.get('case_id'), 'unknown')}`",
        f"Run: `{_text(metadata.get('run_id'), 'unknown')}`",
        "",
    ]

    lines.extend(_render_single_story_section("The decision", _mapping(sections.get("decision"))))
    lines.append("")
    lines.extend(
        _render_what_changed_section(
            starting_direction=_mapping(sections.get("starting_direction")),
            pressure=_mapping(sections.get("what_lolla_pressed_on")),
            changed=_mapping(sections.get("what_changed")),
        )
    )
    lines.append("")
    lines.extend(
        _render_single_story_section(
            "What this means for action",
            _mapping(sections.get("what_this_means_for_action")),
        )
    )
    lines.append("")
    lines.extend(
        _render_single_story_section(
            "What still might be wrong",
            _mapping(sections.get("what_still_might_be_wrong")),
        )
    )
    lines.append("")
    lines.extend(
        _render_single_story_section(
            "What this does not prove",
            _mapping(sections.get("what_was_not_proven")),
        )
    )
    lines.append("")
    lines.extend(_render_evidence_and_limits(brief, sections=sections))

    return "\n".join(lines).rstrip() + "\n"


def write_decision_work_brief_markdown(path: Path | str, markdown: str) -> None:
    """Write rendered Markdown to disk."""

    output_path = Path(path).expanduser()
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkBriefRendererInputError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _render_single_story_section(heading: str, section: Mapping[str, Any]) -> list[str]:
    lines = [f"## {heading}", ""]
    lines.extend(_render_story_section_body(section))
    return lines


def _render_what_changed_section(
    *,
    starting_direction: Mapping[str, Any],
    pressure: Mapping[str, Any],
    changed: Mapping[str, Any],
) -> list[str]:
    lines = ["## What changed", ""]
    lines.extend(_render_story_section_body(starting_direction, label="Starting point"))
    lines.append("")
    lines.extend(_render_story_section_body(pressure, label="What Lolla pressed on"))
    lines.append("")
    lines.extend(_render_story_section_body(changed, label="Change in direction"))
    return lines


def _render_story_section_body(
    section: Mapping[str, Any],
    *,
    label: str | None = None,
) -> list[str]:
    if label:
        lines = [f"**{label}:**"]
    else:
        lines = []
    status = _text(section.get("status"), "missing")
    if status in STATUS_REQUIRING_PLAIN_MISSINGNESS:
        lines.extend(
            [
                f"This part is marked `{status}`. The renderer is not filling or smoothing the missing interpretation.",
            ]
        )
    lines.extend(
        _render_plain_value(
            section.get("value"),
            fallback=_text(section.get("empty_meaning"), "No structured value was supplied."),
            skip_keys=MAIN_BODY_SKIP_KEYS,
        )
    )
    uncertainty = _text(section.get("uncertainty"), "not_assessed")
    if uncertainty != "not_applicable":
        lines.append(f"Uncertainty: {uncertainty}.")
    return lines


def _render_evidence_and_limits(
    brief: Mapping[str, Any],
    *,
    sections: Mapping[str, Any],
) -> list[str]:
    custody = _mapping(brief.get("custody_flags"))
    evidence_section = _mapping(sections.get("evidence_receipt"))
    lines = [
        "## Evidence and limits",
        "",
        "This section preserves source and custody details without putting them in the main decision story.",
        "",
        "### Verification state",
        "",
        f"- Human validation: {_yes_no(custody.get('human_validated'))}",
        f"- Product proof: {_yes_no(custody.get('product_proof'))}",
        f"- Answer-quality scoring: {_yes_no(custody.get('answer_quality_scored'))}",
        f"- Agent action authorization: {_yes_no(custody.get('agent_action_authorized'))}",
        f"- Runtime invoked: {_yes_no(custody.get('runtime_invoked'))}",
        f"- Skill invoked: {_yes_no(custody.get('skill_invoked'))}",
        f"- Archive mutated: {_yes_no(custody.get('archive_mutated'))}",
        f"- Model calls: {_text(custody.get('model_calls'), 'unknown')}",
        f"- Source mode: {_mode_label(brief.get('mode'))}",
        f"- Private/raw content included: {_yes_no(custody.get('raw_private_content_included'))}",
        f"- Provider text included: {_yes_no(custody.get('provider_text_included'))}",
        "",
        "### Source limits",
        "",
    ]
    lines.extend(
        _render_plain_value(
            evidence_section.get("value"),
            fallback=_text(
                evidence_section.get("empty_meaning"),
                "No backing evidence summary was supplied.",
            ),
            skip_keys=set(),
        )
    )
    lines.extend(["", "### Section uncertainty", ""])
    for section_id in SECTION_ORDER:
        section = _mapping(sections.get(section_id))
        lines.append(
            f"- {_sentence_label(SECTION_LABELS[section_id])}: "
            f"{_text(section.get('uncertainty'), 'not_assessed')}"
        )

    source_refs = _collect_source_refs(brief, sections)
    lines.extend(["", "### Source references", ""])
    lines.extend(_render_source_refs(source_refs))
    lines.extend(["", "### Non-claims", ""])
    lines.extend(_render_non_claim_items(brief))
    return lines


def _render_plain_value(
    value: Any,
    *,
    fallback: str,
    skip_keys: set[str],
    indent: int = 0,
) -> list[str]:
    prefix = "  " * indent
    if value is None:
        return [f"{prefix}Value not supplied.", f"{prefix}Empty meaning: {fallback}"]
    if isinstance(value, str):
        return [f"{prefix}{value}"]
    if isinstance(value, bool):
        return [f"{prefix}{_yes_no(value)}"]
    if isinstance(value, (int, float)):
        return [f"{prefix}{value}"]
    if isinstance(value, list):
        if not value:
            return [f"{prefix}Value is an empty list.", f"{prefix}Empty meaning: {fallback}"]
        lines: list[str] = []
        for item in value:
            lines.extend(_render_plain_list_item(item, indent=indent, skip_keys=skip_keys))
        return lines
    if isinstance(value, Mapping):
        if not value:
            return [f"{prefix}Value is an empty object.", f"{prefix}Empty meaning: {fallback}"]
        lines = []
        for key, child in value.items():
            if key in skip_keys:
                continue
            lines.extend(
                _render_plain_mapping_item(
                    str(key),
                    child,
                    indent=indent,
                    skip_keys=skip_keys,
                )
            )
        return lines or [f"{prefix}Value not supplied.", f"{prefix}Empty meaning: {fallback}"]
    return [f"{prefix}{json.dumps(value, ensure_ascii=False, sort_keys=True)}"]


def _render_plain_mapping_item(
    key: str,
    value: Any,
    *,
    indent: int,
    skip_keys: set[str],
) -> list[str]:
    prefix = "  " * indent
    if key in UNLABELED_VALUE_KEYS and isinstance(value, str):
        return [f"{prefix}{value}"]
    label = PLAIN_LABELS.get(key, _humanize_key(key))
    if isinstance(value, list):
        lines = [f"{prefix}{label}:"]
        lines.extend(_render_plain_value(value, fallback="No structured value was supplied.", skip_keys=skip_keys, indent=indent))
        return lines
    if isinstance(value, Mapping):
        lines = [f"{prefix}{label}:"]
        lines.extend(_render_plain_value(value, fallback="No structured value was supplied.", skip_keys=skip_keys, indent=indent + 1))
        return lines
    if value is None:
        return [f"{prefix}{label}: not supplied"]
    if isinstance(value, bool):
        return [f"{prefix}{label}: {_yes_no(value)}"]
    if isinstance(value, (int, float)):
        return [f"{prefix}{label}: {value}"]
    return [f"{prefix}{label}: {str(value)}"]


def _render_plain_list_item(
    value: Any,
    *,
    indent: int,
    skip_keys: set[str],
) -> list[str]:
    prefix = "  " * indent
    if isinstance(value, (Mapping, list)):
        lines = [f"{prefix}-"]
        lines.extend(
            _render_plain_value(
                value,
                fallback="No structured value was supplied.",
                skip_keys=skip_keys,
                indent=indent + 1,
            )
        )
        return lines
    if value is None:
        return [f"{prefix}- not supplied"]
    if isinstance(value, bool):
        return [f"{prefix}- {_yes_no(value)}"]
    if isinstance(value, (int, float)):
        return [f"{prefix}- {value}"]
    return [f"{prefix}- {str(value)}"]


def _collect_source_refs(
    brief: Mapping[str, Any],
    sections: Mapping[str, Any],
) -> list[Any]:
    refs = [*_list(brief.get("source_refs"))]
    evidence_section = _mapping(sections.get("evidence_receipt"))
    refs.extend(_list(evidence_section.get("source_refs")))
    seen: set[tuple[str, str, str]] = set()
    unique_refs: list[Any] = []
    for raw_ref in refs:
        ref = _mapping(raw_ref)
        key = (
            _text(ref.get("artifact"), "unknown artifact"),
            _text(ref.get("field"), "unknown field"),
            _text(ref.get("source_status"), "unknown"),
        )
        if key in seen:
            continue
        seen.add(key)
        unique_refs.append(raw_ref)
    return unique_refs


def _render_value(value: Any, *, fallback: str, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    if value is None:
        return [f"{prefix}Value: not supplied.", f"{prefix}Empty meaning: {fallback}"]
    if isinstance(value, str):
        return [f"{prefix}{value}"]
    if isinstance(value, bool):
        return [f"{prefix}`{str(value).lower()}`"]
    if isinstance(value, (int, float)):
        return [f"{prefix}`{value}`"]
    if isinstance(value, list):
        if not value:
            return [f"{prefix}Value: empty list.", f"{prefix}Empty meaning: {fallback}"]
        lines: list[str] = []
        for item in value:
            lines.extend(_render_list_item(item, indent=indent))
        return lines
    if isinstance(value, Mapping):
        if not value:
            return [f"{prefix}Value: empty object.", f"{prefix}Empty meaning: {fallback}"]
        lines = []
        for key, child in value.items():
            lines.extend(_render_mapping_item(str(key), child, indent=indent))
        return lines
    return [f"{prefix}{json.dumps(value, ensure_ascii=False, sort_keys=True)}"]


def _render_mapping_item(key: str, value: Any, *, indent: int) -> list[str]:
    prefix = "  " * indent
    if isinstance(value, (Mapping, list)):
        lines = [f"{prefix}- `{key}`:"]
        lines.extend(_render_value(value, fallback="No structured value was supplied.", indent=indent + 1))
        return lines
    if value is None:
        return [f"{prefix}- `{key}`: not supplied"]
    if isinstance(value, bool):
        return [f"{prefix}- `{key}`: `{str(value).lower()}`"]
    if isinstance(value, (int, float)):
        return [f"{prefix}- `{key}`: `{value}`"]
    return [f"{prefix}- `{key}`: {str(value)}"]


def _render_list_item(value: Any, *, indent: int) -> list[str]:
    prefix = "  " * indent
    if isinstance(value, (Mapping, list)):
        lines = [f"{prefix}-"]
        lines.extend(_render_value(value, fallback="No structured value was supplied.", indent=indent + 1))
        return lines
    if value is None:
        return [f"{prefix}- not supplied"]
    if isinstance(value, bool):
        return [f"{prefix}- `{str(value).lower()}`"]
    if isinstance(value, (int, float)):
        return [f"{prefix}- `{value}`"]
    return [f"{prefix}- {str(value)}"]


def _render_source_refs(source_refs: list[Any]) -> list[str]:
    if not source_refs:
        return ["- none supplied"]
    lines: list[str] = []
    for raw_ref in source_refs:
        ref = _mapping(raw_ref)
        artifact = _text(ref.get("artifact"), "unknown artifact")
        field = _text(ref.get("field"), "unknown field")
        status = _text(ref.get("source_status"), "unknown")
        lines.append(f"- `{artifact}` / `{field}` (source status: `{status}`)")
    return lines


def _render_non_claims(brief: Mapping[str, Any]) -> list[str]:
    non_claims = _mapping(brief.get("non_claims"))
    items = [item for item in _list(non_claims.get("items")) if isinstance(item, str)]
    lines = ["## What This Must Not Claim", ""]
    if not items:
        lines.append("- No explicit non-claims were supplied; treat this brief as incomplete.")
        return lines
    lines.extend(f"- `{item}`" for item in items)
    return lines


def _render_non_claim_items(brief: Mapping[str, Any]) -> list[str]:
    non_claims = _mapping(brief.get("non_claims"))
    items = [item for item in _list(non_claims.get("items")) if isinstance(item, str)]
    if not items:
        return ["- No explicit non-claims were supplied; treat this brief as incomplete."]
    return [f"- `{item}`" for item in items]


def _render_custody_flags(custody: Mapping[str, Any]) -> list[str]:
    if not custody:
        return ["- No custody flags supplied; treat this brief as incomplete."]
    lines: list[str] = []
    for field in CUSTODY_FLAG_ORDER:
        if field in custody:
            value = custody[field]
            if isinstance(value, bool):
                rendered = str(value).lower()
            else:
                rendered = str(value)
            lines.append(f"- `{field}`: `{rendered}`")
    human_status = custody.get("human_validation_status")
    if isinstance(human_status, str):
        lines.append(f"- `human_validation_status`: `{human_status}`")
    return lines


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _text(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    return fallback


def _bool_text(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return "unknown"


def _yes_no(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    return "unknown"


def _mode_label(value: Any) -> str:
    mode = _text(value, "unknown")
    labels = {
        "checked_in_safe_mode": "checked-in-safe",
        "local_private_mode": "local-private",
        "future_runtime_mode_not_implemented": "future runtime mode not implemented",
    }
    return labels.get(mode, mode)


def _humanize_key(key: str) -> str:
    return key.replace("_", " ").capitalize()


def _sentence_label(value: str) -> str:
    if not value:
        return value
    return value[0].upper() + value[1:]
