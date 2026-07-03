"""Markdown renderer for PR186 generated-read brief supply packets.

PR187 renders one offline, reader-facing Markdown brief from a ready PR186
supply packet. It is deterministic: it validates and formats supplied fields,
source refs, uncertainty, privacy limits, and non-claims. It does not add
semantic interpretation, enrich briefs, generate triage, mark resolver refs
usable, update sidecars, call models, score advice, claim proof, or authorize
action.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_generated_read_brief_supply import (
    READY_STATUS,
    SUPPLY_SCHEMA_VERSION,
)


RENDER_STATUS = "rendered_from_generated_read_supply"
NON_CLAIMS = (
    "rendering_is_deterministic_formatting_only",
    "rendering_does_not_generate_interpretation",
    "rendering_does_not_enrich_briefs",
    "rendering_does_not_generate_triage",
    "rendering_does_not_mark_resolver_refs_usable",
    "rendering_does_not_update_runtime_sidecars",
    "rendering_is_not_product_proof",
    "rendering_is_not_human_validation",
    "rendering_does_not_score_answer_quality",
    "rendering_does_not_validate_advice_correctness",
    "rendering_does_not_authorize_agent_action",
    "rendering_does_not_authorize_automatic_action",
)
REQUIRED_DOWNSTREAM_FALSE = (
    "can_update_sidecar",
    "can_authorize_agent_action",
    "can_be_used_as_quality_label",
)
REQUIRED_CUSTODY_FALSE = (
    "product_proof",
    "human_validated",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
)
PRIVATE_MARKERS = (
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
    "/" + "Users" + "/",
)


class DecisionWorkGeneratedReadBriefRendererError(ValueError):
    """Sanitized generated-read brief rendering error."""


def load_generated_read_brief_supply(path: Path | str) -> dict[str, Any]:
    """Load a generated-read brief supply JSON object."""

    input_path = Path(path).expanduser()
    try:
        text = input_path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except FileNotFoundError as exc:
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply JSON file was not found"
        ) from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply JSON file was malformed"
        ) from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply JSON file was not valid UTF-8"
        ) from exc
    except OSError as exc:
        raise DecisionWorkGeneratedReadBriefRendererError(
            f"supply JSON file could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply JSON root was not an object"
        )
    if _contains_private_marker(text):
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply JSON contained a forbidden privacy marker"
        )
    validate_generated_read_brief_supply(payload)
    return payload


def validate_generated_read_brief_supply(supply: Mapping[str, Any]) -> None:
    """Validate the renderer's required subset of the PR186 supply packet."""

    if supply.get("schema_version") != SUPPLY_SCHEMA_VERSION:
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply schema version was unsupported"
        )
    if supply.get("supply_status") != READY_STATUS:
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply status was not ready for offline brief rendering"
        )
    blockers = supply.get("blocker_reasons")
    if blockers not in ([], None):
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply had blocker reasons"
        )
    allowed = supply.get("allowed_brief_feed")
    if not isinstance(allowed, list) or not allowed:
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply allowed_brief_feed was missing"
        )
    for field in allowed:
        _validate_feed_field(_mapping(field))

    downstream = _mapping(supply.get("downstream_allowed"))
    if downstream.get("can_render_offline_brief") is not True:
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply did not allow offline brief rendering"
        )
    for key in REQUIRED_DOWNSTREAM_FALSE:
        if downstream.get(key) is not False:
            raise DecisionWorkGeneratedReadBriefRendererError(
                f"supply downstream boundary was unsafe:{key}"
            )

    custody = _mapping(supply.get("custody_flags"))
    if _safe_int(custody.get("model_calls")) != 0:
        raise DecisionWorkGeneratedReadBriefRendererError(
            "supply custody claimed model calls"
        )
    for key in REQUIRED_CUSTODY_FALSE:
        if custody.get(key) is not False:
            raise DecisionWorkGeneratedReadBriefRendererError(
                f"supply custody boundary was unsafe:{key}"
            )


def render_generated_read_brief_markdown(
    *,
    supply: Mapping[str, Any],
    case_id: str = "launch-public-enterprise-beta",
) -> str:
    """Render a ready generated-read brief supply packet as Markdown."""

    validate_generated_read_brief_supply(supply)
    fields = _field_map(_list(supply.get("allowed_brief_feed")))
    evidence_only = [str(item) for item in _list(supply.get("evidence_only_fields"))]
    custody = _mapping(supply.get("custody_flags"))
    downstream = _mapping(supply.get("downstream_allowed"))

    lines = [
        "# Decision Work Generated Read Brief",
        "",
        (
            "This is a provisional offline brief rendered from a PR186 "
            "generated-read supply packet. It formats supplied fields only; it "
            "is not proof that the interpretation is true or that the advice is "
            "correct."
        ),
        "",
        f"Case: `{case_id}`",
        f"Source read: `{_text(supply.get('source_read_ref'), 'not supplied')}`",
        f"Intake result: `{_text(supply.get('intake_ref'), 'not supplied')}`",
        f"Supply status: `{_text(supply.get('supply_status'), 'unknown')}`",
        "",
    ]

    lines.extend(_render_field_section("The decision", fields.get("decision_question")))
    lines.append("")
    lines.extend(
        _render_generated_interpretation_section(
            fields=fields,
            evidence_only=evidence_only,
        )
    )
    lines.append("")
    lines.extend(
        _render_field_section(
            "What changed for action",
            fields.get("revised_direction_or_action_consequence"),
        )
    )
    lines.append("")
    lines.extend(_render_what_might_be_wrong(supply=supply, evidence_only=evidence_only))
    lines.append("")
    lines.extend(
        _render_field_section(
            "What this does not prove",
            fields.get("what_the_final_answer_does_not_prove"),
        )
    )
    lines.append("")
    lines.extend(
        _render_evidence_and_limits(
            fields=fields,
            supply=supply,
            custody=custody,
            downstream=downstream,
            evidence_only=evidence_only,
        )
    )
    rendered = "\n".join(lines).rstrip() + "\n"
    if _contains_private_marker(rendered):
        raise DecisionWorkGeneratedReadBriefRendererError(
            "rendered Markdown contained a forbidden privacy marker"
        )
    return rendered


def write_generated_read_brief_markdown(path: Path | str, markdown: str) -> None:
    """Write rendered generated-read Markdown."""

    output = Path(path).expanduser()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkGeneratedReadBriefRendererError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def _validate_feed_field(field: Mapping[str, Any]) -> None:
    if not _text(field.get("field_name")):
        raise DecisionWorkGeneratedReadBriefRendererError("feed field was unnamed")
    if not _text(field.get("uncertainty")):
        raise DecisionWorkGeneratedReadBriefRendererError(
            "feed field was missing uncertainty"
        )
    if not _text(field.get("source_status")):
        raise DecisionWorkGeneratedReadBriefRendererError(
            "feed field was missing source status"
        )
    if not _text(field.get("interpretation_basis")):
        raise DecisionWorkGeneratedReadBriefRendererError(
            "feed field was missing interpretation basis"
        )
    if not _text(field.get("privacy_limit")):
        raise DecisionWorkGeneratedReadBriefRendererError(
            "feed field was missing privacy limit"
        )
    if field.get("must_not_be_used_as_quality_label") is not True:
        raise DecisionWorkGeneratedReadBriefRendererError(
            "feed field could be used as a quality label"
        )
    source_refs = field.get("source_refs")
    if not isinstance(source_refs, list) or not source_refs:
        raise DecisionWorkGeneratedReadBriefRendererError(
            "feed field was missing source refs"
        )


def _render_field_section(heading: str, field: Mapping[str, Any] | None) -> list[str]:
    lines = [f"## {heading}", ""]
    if not field:
        lines.append("Not supplied. The renderer does not infer this section.")
        return lines
    lines.append(_text(field.get("value"), "Value not supplied."))
    lines.append("")
    lines.append(f"Uncertainty: {_text(field.get('uncertainty'), 'not supplied')}.")
    lines.append(f"Source status: {_text(field.get('source_status'), 'not supplied')}.")
    lines.append(
        f"Interpretation basis: {_text(field.get('interpretation_basis'), 'not supplied')}."
    )
    lines.append(f"Privacy limit: {_text(field.get('privacy_limit'), 'not supplied')}")
    return lines


def _render_generated_interpretation_section(
    *,
    fields: Mapping[str, Mapping[str, Any]],
    evidence_only: list[str],
) -> list[str]:
    lines = ["## What the generated interpretation adds", ""]
    optional_order = (
        "likely_starting_direction",
        "decision_thresholds",
        "evidence_gates",
        "useful_friction",
    )
    used = False
    for field_name in optional_order:
        field = fields.get(field_name)
        if not field:
            continue
        used = True
        lines.append(f"**{_humanize(field_name)}:** {_text(field.get('value'))}")
        lines.append(f"Uncertainty: {_text(field.get('uncertainty'), 'not supplied')}.")
        lines.append("")
    if not used:
        lines.append(
            "The ready supply packet does not add optional brief-feed fields beyond "
            "the decision, action consequence, evidence gates, and non-claim "
            "boundary. The renderer does not fill missing fields."
        )
        lines.append("")
    lines.append("Evidence-only fields excluded from the user-facing brief feed:")
    for field_name in evidence_only:
        lines.append(f"- `{field_name}`")
    return lines


def _render_what_might_be_wrong(
    *,
    supply: Mapping[str, Any],
    evidence_only: list[str],
) -> list[str]:
    lines = [
        "## What still might be wrong",
        "",
        (
            "This brief is rendered from a checked-in-safe generated-read supply "
            "packet, not from full private conversation context. Missing or "
            "evidence-only fields may change the interpretation if reviewed later."
        ),
        "",
        "Known limits:",
        f"- Missing required fields: {_csv(_list(supply.get('missing_required_fields')))}",
        f"- Evidence-only fields excluded: {_csv(evidence_only)}",
        "- Human review is still required before treating the brief as operational guidance.",
        "- Sidecar updates, resolver ref use, triage, enrichment, and action authorization remain out of scope.",
    ]
    return lines


def _render_evidence_and_limits(
    *,
    fields: Mapping[str, Mapping[str, Any]],
    supply: Mapping[str, Any],
    custody: Mapping[str, Any],
    downstream: Mapping[str, Any],
    evidence_only: list[str],
) -> list[str]:
    lines = [
        "## Evidence and limits",
        "",
        "### Verification state",
        "",
        f"- Product proof: {_yes_no(custody.get('product_proof'))}",
        f"- Human validation: {_yes_no(custody.get('human_validated'))}",
        f"- Answer-quality scoring: {_yes_no(custody.get('answer_quality_scored'))}",
        f"- Agent action authorization: {_yes_no(custody.get('agent_action_authorized'))}",
        f"- Automatic action authorization: {_yes_no(custody.get('automatic_action_authorized'))}",
        f"- Runtime sidecar update allowed: {_yes_no(downstream.get('can_update_sidecar'))}",
        f"- Runtime invoked: {_yes_no(custody.get('runtime_invoked'))}",
        f"- Skill invoked: {_yes_no(custody.get('skill_invoked'))}",
        f"- Model calls: {_text(custody.get('model_calls'), 'unknown')}",
        "",
        "### Source summary",
        "",
        f"- Source refs preserved: {_yes_no(_mapping(supply.get('source_ref_summary')).get('source_refs_preserved'))}",
        f"- Checked source refs: {_text(_mapping(supply.get('source_ref_summary')).get('checked_source_ref_count'), '0')}",
        f"- Privacy status: {_text(_mapping(supply.get('privacy_summary')).get('status'), 'unknown')}",
        f"- Uncertainty status: {_text(_mapping(supply.get('uncertainty_summary')).get('status'), 'unknown')}",
        "",
        "### Source references",
        "",
    ]
    lines.extend(_render_source_refs(fields))
    lines.extend(
        [
            "",
            "### Allowed fields used",
            "",
        ]
    )
    for field_name in fields:
        lines.append(f"- `{field_name}`")
    lines.extend(
        [
            "",
            "### Evidence-only fields excluded",
            "",
        ]
    )
    for field_name in evidence_only:
        lines.append(f"- `{field_name}`")
    lines.extend(["", "### Non-claims", ""])
    for claim in [*_list(supply.get("non_claims")), *NON_CLAIMS]:
        lines.append(f"- `{claim}`")
    return lines


def _render_source_refs(fields: Mapping[str, Mapping[str, Any]]) -> list[str]:
    refs: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    for field_name, field in fields.items():
        for raw_ref in _list(field.get("source_refs")):
            ref = _mapping(raw_ref)
            artifact = _text(ref.get("artifact"), "unknown artifact")
            locator = _text(ref.get("locator"), "unknown locator")
            source_status = _text(ref.get("source_status"), "unknown source status")
            key = (artifact, locator, source_status)
            if key in seen:
                continue
            seen.add(key)
            refs.append(
                f"- `{artifact}` / `{locator}` for `{field_name}` "
                f"(source status: `{source_status}`)"
            )
    return refs or ["- No source refs supplied."]


def _field_map(fields: list[Any]) -> dict[str, Mapping[str, Any]]:
    mapped: dict[str, Mapping[str, Any]] = {}
    for field in fields:
        item = _mapping(field)
        field_name = _text(item.get("field_name"))
        if field_name:
            mapped[field_name] = item
    return mapped


def _contains_private_marker(text: str) -> bool:
    return any(marker in text for marker in PRIVATE_MARKERS)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    return default


def _safe_int(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return 0


def _yes_no(value: Any) -> str:
    return "yes" if value is True else "no"


def _csv(values: list[Any]) -> str:
    if not values:
        return "none"
    return ", ".join(f"`{value}`" for value in values)


def _humanize(value: str) -> str:
    return value.replace("_", " ").capitalize()
