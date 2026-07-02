"""Offline enrichment builder for Decision Work Brief Markdown.

This module applies an existing interpretation read to an existing rendered
Decision Work Brief using an explicit rules contract. It does not interpret new
fields, call models, invoke Lolla, mutate archives, or change runtime behavior.
"""
from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


RULES_SCHEMA_VERSION = "lolla.decision_work_brief_enrichment_rules_contract.v0"
SUPPORTED_INTERPRETATION_READ_SCHEMA_VERSIONS = {
    "lolla.decision_work_conversation_interpretation_tiny_offline_read.v0",
    "lolla.decision_work_conversation_interpretation_second_tiny_offline_read.v0",
    "lolla.decision_work_conversation_interpretation_read.v0",
}
CONSERVATIVE_FALSE_CUSTODY_FLAGS = (
    "human_validated",
    "product_proof",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
    "answer_quality_scored",
    "agent_action_authorized",
    "raw_private_content_checked_in",
    "provider_text_checked_in",
)
FORBIDDEN_USER_FACING_CONCEPTS = {
    "answer_quality_score",
    "improvement_score",
    "winner",
    "approval",
    "certification",
    "agent_action_authorization",
    "product_proof",
    "human_validated_without_actual_human_review",
}
SKIPPED_FIELD_STATUSES = {"insufficient_context", "not_interpreted", "not_applicable"}


class DecisionWorkBriefEnrichmentInputError(ValueError):
    """Sanitized enrichment input error."""


def load_json_object(path: Path | str) -> dict[str, Any]:
    """Load a JSON object with sanitized input errors."""

    input_path = Path(path).expanduser()
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DecisionWorkBriefEnrichmentInputError("input JSON file was not found") from exc
    except json.JSONDecodeError as exc:
        raise DecisionWorkBriefEnrichmentInputError("input JSON file was malformed") from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkBriefEnrichmentInputError(
            "input JSON file was not valid UTF-8"
        ) from exc
    except OSError as exc:
        raise DecisionWorkBriefEnrichmentInputError(
            f"input JSON file could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise DecisionWorkBriefEnrichmentInputError("input JSON root was not an object")
    return payload


def load_markdown(path: Path | str) -> str:
    """Load Markdown with sanitized input errors."""

    input_path = Path(path).expanduser()
    try:
        return input_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DecisionWorkBriefEnrichmentInputError("input Markdown file was not found") from exc
    except UnicodeDecodeError as exc:
        raise DecisionWorkBriefEnrichmentInputError(
            "input Markdown file was not valid UTF-8"
        ) from exc
    except OSError as exc:
        raise DecisionWorkBriefEnrichmentInputError(
            f"input Markdown file could not be read:{type(exc).__name__}"
        ) from exc


def write_enriched_decision_work_brief_markdown(path: Path | str, markdown: str) -> None:
    """Write enriched Markdown to disk."""

    output_path = Path(path).expanduser()
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        raise DecisionWorkBriefEnrichmentInputError(
            f"output could not be written:{type(exc).__name__}"
        ) from exc


def validate_rules_contract(rules: Mapping[str, Any]) -> None:
    """Validate the subset of the PR139 rules contract required by the builder."""

    if rules.get("schema_version") != RULES_SCHEMA_VERSION:
        raise DecisionWorkBriefEnrichmentInputError("rules schema version was unsupported")
    allowed_fields = _rules_field_names(rules.get("allowed_user_facing_fields"))
    evidence_only_fields = set(_field_name_list(rules.get("evidence_only_fields")))
    forbidden_fields = _forbidden_concepts(rules.get("forbidden_fields"))
    if not allowed_fields:
        raise DecisionWorkBriefEnrichmentInputError("rules allowed field set was empty")
    if allowed_fields & evidence_only_fields:
        raise DecisionWorkBriefEnrichmentInputError(
            "rules allowed evidence-only fields in user-facing enrichment"
        )
    if allowed_fields & forbidden_fields:
        raise DecisionWorkBriefEnrichmentInputError(
            "rules allowed forbidden fields in user-facing enrichment"
        )
    if not FORBIDDEN_USER_FACING_CONCEPTS <= forbidden_fields:
        raise DecisionWorkBriefEnrichmentInputError(
            "rules forbidden field policy was incomplete"
        )

    section_rules = rules.get("enrichment_section_rules")
    if not isinstance(section_rules, Mapping):
        raise DecisionWorkBriefEnrichmentInputError("rules enrichment section was missing")
    for required_bool in (
        "must_include_uncertainty",
        "must_include_non_claim",
        "must_not_include_field_dump",
    ):
        if section_rules.get(required_bool) is not True:
            raise DecisionWorkBriefEnrichmentInputError(
                "rules enrichment section was not conservative"
            )

    builder_requirements = rules.get("builder_requirements")
    if not isinstance(builder_requirements, Mapping):
        raise DecisionWorkBriefEnrichmentInputError("rules builder requirements were missing")
    for required_bool in (
        "must_accept_original_rendered_brief",
        "must_accept_interpretation_read",
        "must_accept_enrichment_rules_contract",
        "must_output_separate_enriched_markdown",
        "must_preserve_original_brief_unchanged",
        "must_include_only_allowed_user_facing_fields",
        "must_list_excluded_fields_in_evidence_and_limits_or_review",
        "must_preserve_non_claims",
        "must_preserve_source_privacy_limits",
        "must_not_call_models",
        "must_not_invoke_runtime",
        "must_not_run_lolla",
        "must_not_mutate_archives",
    ):
        if builder_requirements.get(required_bool) is not True:
            raise DecisionWorkBriefEnrichmentInputError(
                "rules builder requirements were not conservative"
            )


def validate_interpretation_read(read: Mapping[str, Any]) -> None:
    """Validate an interpretation read before using it for enrichment."""

    if read.get("schema_version") not in SUPPORTED_INTERPRETATION_READ_SCHEMA_VERSIONS:
        raise DecisionWorkBriefEnrichmentInputError(
            "interpretation read schema version was unsupported"
        )
    custody_flags = read.get("custody_flags")
    if not isinstance(custody_flags, Mapping):
        raise DecisionWorkBriefEnrichmentInputError(
            "interpretation read custody flags were missing"
        )
    for flag in CONSERVATIVE_FALSE_CUSTODY_FLAGS:
        if custody_flags.get(flag) is not False:
            raise DecisionWorkBriefEnrichmentInputError(
                "interpretation read custody flags were not conservative"
            )
    if custody_flags.get("model_calls") != 0:
        raise DecisionWorkBriefEnrichmentInputError(
            "interpretation read model call count was not conservative"
        )
    if custody_flags.get("semantic_read_is_provisional") is not True:
        raise DecisionWorkBriefEnrichmentInputError(
            "interpretation read was not marked provisional"
        )
    if not isinstance(read.get("interpreted_fields"), list):
        raise DecisionWorkBriefEnrichmentInputError(
            "interpretation read interpreted_fields were missing"
        )


def enrich_decision_work_brief_markdown(
    *,
    brief_markdown: str,
    interpretation_read: Mapping[str, Any],
    rules_contract: Mapping[str, Any],
) -> str:
    """Return enriched Markdown using only existing read fields and PR139 rules."""

    validate_rules_contract(rules_contract)
    validate_interpretation_read(interpretation_read)
    if "## Evidence and limits" not in brief_markdown:
        raise DecisionWorkBriefEnrichmentInputError(
            "brief Markdown was missing Evidence and limits"
        )
    if "## What this does not prove" not in brief_markdown:
        raise DecisionWorkBriefEnrichmentInputError(
            "brief Markdown was missing non-claim section"
        )

    allowed_fields = _rules_field_names(rules_contract.get("allowed_user_facing_fields"))
    evidence_only_fields = set(_field_name_list(rules_contract.get("evidence_only_fields")))
    fields_by_name = _interpreted_fields_by_name(interpretation_read)
    included_fields = _eligible_user_facing_fields(
        allowed_fields=allowed_fields,
        fields_by_name=fields_by_name,
    )
    if not included_fields:
        raise DecisionWorkBriefEnrichmentInputError(
            "interpretation read did not contain eligible user-facing fields"
        )

    without_old_enrichment = _remove_markdown_section(
        brief_markdown,
        heading="What the interpretation adds",
    )
    with_enrichment = _insert_before_heading(
        without_old_enrichment,
        heading="What still might be wrong",
        insertion=_render_enrichment_section(included_fields),
    )
    with_limits = _insert_interpretation_limits(
        with_enrichment,
        included_fields=included_fields,
        evidence_only_fields=sorted(evidence_only_fields),
        interpretation_read=interpretation_read,
    )
    return with_limits.rstrip() + "\n"


def enrich_decision_work_brief_from_paths(
    *,
    brief_path: Path | str,
    interpretation_read_path: Path | str,
    rules_path: Path | str,
    output_path: Path | str,
) -> None:
    """Enrich a brief from paths and write a separate Markdown output."""

    brief_resolved = Path(brief_path).expanduser().resolve()
    output_resolved = Path(output_path).expanduser().resolve()
    if brief_resolved == output_resolved:
        raise DecisionWorkBriefEnrichmentInputError(
            "output path must be different from input brief"
        )
    brief_markdown = load_markdown(brief_path)
    interpretation_read = load_json_object(interpretation_read_path)
    rules_contract = load_json_object(rules_path)
    enriched = enrich_decision_work_brief_markdown(
        brief_markdown=brief_markdown,
        interpretation_read=interpretation_read,
        rules_contract=rules_contract,
    )
    write_enriched_decision_work_brief_markdown(output_path, enriched)


def _rules_field_names(value: Any) -> set[str]:
    if not isinstance(value, list):
        raise DecisionWorkBriefEnrichmentInputError("rules field list was malformed")
    field_names: set[str] = set()
    for item in value:
        if not isinstance(item, Mapping):
            raise DecisionWorkBriefEnrichmentInputError("rules field entry was malformed")
        field_name = item.get("field_name")
        if not isinstance(field_name, str) or not field_name:
            raise DecisionWorkBriefEnrichmentInputError("rules field name was malformed")
        for required_bool in (
            "source_refs_required",
            "source_status_required",
            "uncertainty_required",
            "interpretation_basis_required",
            "privacy_limit_required",
            "human_review_required_flag_required",
            "must_not_be_used_as_quality_label",
        ):
            if item.get(required_bool) is not True:
                raise DecisionWorkBriefEnrichmentInputError(
                    "rules field requirements were incomplete"
                )
        field_names.add(field_name)
    return field_names


def _forbidden_concepts(value: Any) -> set[str]:
    if not isinstance(value, list):
        raise DecisionWorkBriefEnrichmentInputError("rules forbidden field list was malformed")
    concepts: set[str] = set()
    for item in value:
        if isinstance(item, str):
            concepts.add(item)
        elif isinstance(item, Mapping) and isinstance(item.get("concept"), str):
            concepts.add(item["concept"])
        else:
            raise DecisionWorkBriefEnrichmentInputError(
                "rules forbidden field entry was malformed"
            )
    return concepts


def _field_name_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise DecisionWorkBriefEnrichmentInputError("rules string list was malformed")
    strings: list[str] = []
    for item in value:
        if isinstance(item, str):
            strings.append(item)
            continue
        if isinstance(item, Mapping) and isinstance(item.get("field_name"), str):
            strings.append(item["field_name"])
            continue
        else:
            raise DecisionWorkBriefEnrichmentInputError("rules string entry was malformed")
    return strings


def _interpreted_fields_by_name(read: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    fields: dict[str, Mapping[str, Any]] = {}
    for item in read.get("interpreted_fields", []):
        if not isinstance(item, Mapping):
            raise DecisionWorkBriefEnrichmentInputError(
                "interpretation field entry was malformed"
            )
        field_name = item.get("field_name")
        if not isinstance(field_name, str) or not field_name:
            raise DecisionWorkBriefEnrichmentInputError(
                "interpretation field name was malformed"
            )
        if not isinstance(item.get("source_refs"), list) or not item["source_refs"]:
            raise DecisionWorkBriefEnrichmentInputError(
                "interpretation field source refs were missing"
            )
        if item.get("must_not_be_used_as_quality_label") is not True:
            raise DecisionWorkBriefEnrichmentInputError(
                "interpretation field was not protected from quality-label use"
            )
        fields[field_name] = item
    return fields


def _eligible_user_facing_fields(
    *,
    allowed_fields: set[str],
    fields_by_name: Mapping[str, Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    included: dict[str, Mapping[str, Any]] = {}
    for field_name in sorted(allowed_fields):
        field = fields_by_name.get(field_name)
        if field is None:
            continue
        if field.get("status") in SKIPPED_FIELD_STATUSES:
            continue
        if field.get("could_feed_brief") is not True:
            continue
        included[field_name] = field
    return included


def _render_enrichment_section(fields: Mapping[str, Mapping[str, Any]]) -> str:
    decision = _clean_field_value(fields, "decision_question")
    starting = _clean_field_value(fields, "likely_starting_direction")
    action = _clean_field_value(fields, "revised_direction_or_action_consequence")
    thresholds = _clean_field_value(fields, "decision_thresholds")
    gates = _clean_field_value(fields, "evidence_gates")
    friction = _clean_field_value(fields, "useful_friction")
    non_proof = _clean_field_value(fields, "what_the_final_answer_does_not_prove")

    paragraphs: list[str] = []
    context_parts: list[str] = []
    if decision:
        context_parts.append(f"The decision is framed as: {decision}")
    if starting:
        context_parts.append(
            f"The starting point remains uncertain: {starting}"
        )
    if context_parts:
        context_parts.append(
            "Checked-in-safe sources are compressed, so this should be read as a limited clarification, not as a settled account of what was already present."
        )
        paragraphs.append(" ".join(context_parts))

    action_parts: list[str] = []
    if action:
        action_parts.append(f"What becomes clearer for action: {action}")
    if thresholds:
        action_parts.append(f"The visible thresholds are: {thresholds}")
    if gates:
        action_parts.append(f"The evidence gates are: {gates}")
    if action_parts:
        paragraphs.append(" ".join(action_parts))

    caution_parts: list[str] = []
    if friction:
        caution_parts.append(f"What appears sharpened as a descriptive caution: {friction}")
    if non_proof:
        caution_parts.append(f"This must not be used to prove more than the sources support: {non_proof}")
    caution_parts.append(
        "This enrichment remains provisional and does not prove Lolla improved the decision."
    )
    paragraphs.append(" ".join(caution_parts))

    lines = ["## What the interpretation adds", ""]
    for index, paragraph in enumerate(paragraphs[:3]):
        if index:
            lines.append("")
        lines.append(_normalize_space(paragraph))
    return "\n".join(lines) + "\n\n"


def _insert_interpretation_limits(
    markdown: str,
    *,
    included_fields: Mapping[str, Mapping[str, Any]],
    evidence_only_fields: Sequence[str],
    interpretation_read: Mapping[str, Any],
) -> str:
    section = _render_interpretation_limits(
        included_fields=included_fields,
        evidence_only_fields=evidence_only_fields,
        interpretation_read=interpretation_read,
    )
    cleaned = _remove_markdown_subsection(
        markdown,
        heading="Interpretation enrichment limits",
    )
    return _insert_after_heading_intro(
        cleaned,
        heading="Evidence and limits",
        insertion=section,
    )


def _render_interpretation_limits(
    *,
    included_fields: Mapping[str, Mapping[str, Any]],
    evidence_only_fields: Sequence[str],
    interpretation_read: Mapping[str, Any],
) -> str:
    source_packet = interpretation_read.get("source_packet")
    packet_mode = "checked_in_safe"
    packet_checked_in = False
    if isinstance(source_packet, Mapping):
        packet_mode = str(source_packet.get("packet_generation_mode", packet_mode))
        packet_checked_in = source_packet.get("packet_checked_in") is True

    source_refs = _compact_source_refs(included_fields.values())
    source_refs_text = ", ".join(f"`{ref}`" for ref in source_refs) if source_refs else "none"
    included_text = ", ".join(f"`{name}`" for name in sorted(included_fields))
    evidence_only_text = ", ".join(f"`{name}`" for name in evidence_only_fields)
    uncertainties = sorted(
        {
            str(field.get("uncertainty"))
            for field in included_fields.values()
            if field.get("uncertainty")
        }
    )
    uncertainty_text = ", ".join(f"`{item}`" for item in uncertainties)

    return "\n".join(
        [
            "### Interpretation enrichment limits",
            "",
            f"- Enrichment source mode: `{packet_mode}`",
            f"- Source packet checked in: {'yes' if packet_checked_in else 'no'}",
            "- Model calls: 0",
            "- Runtime invoked: no",
            "- Skill invoked: no",
            "- Raw/private content checked in: no",
            "- Provider text checked in: no",
            f"- Included interpretation fields: {included_text}",
            f"- Evidence-only fields excluded from the main enrichment section: {evidence_only_text}",
            f"- Included-field uncertainty levels: {uncertainty_text}",
            f"- Compact source refs: {source_refs_text}",
            "- Human review required before treating the enrichment as user-facing validation: yes",
            "- Non-claim: this enrichment is provisional and is not proof of decision improvement.",
            "",
        ]
    )


def _field_value(fields: Mapping[str, Mapping[str, Any]], field_name: str) -> str | None:
    field = fields.get(field_name)
    if field is None:
        return None
    value = field.get("value")
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def _clean_field_value(
    fields: Mapping[str, Mapping[str, Any]],
    field_name: str,
) -> str | None:
    value = _field_value(fields, field_name)
    if value is None:
        return None
    cleaned = value
    replacements = (
        (
            r"^The decision appears to be whether to ",
            "whether to ",
        ),
        (
            r"^The action consequence is to ",
            "to ",
        ),
        (
            r"^Visible thresholds include ",
            "",
        ),
        (
            r"^The visible evidence gates are ",
            "",
        ),
        (
            r"^Visible evidence gates include ",
            "",
        ),
        (
            r"^The useful friction appears to be ",
            "",
        ),
        (
            r"\s*This is a provisional description, not a quality score\.$",
            "",
        ),
        (
            r"^The final answer and brief do not prove ",
            "the final answer and brief do not prove ",
        ),
    )
    for pattern, replacement in replacements:
        cleaned = re.sub(pattern, replacement, cleaned)
    return _normalize_space(cleaned)


def _compact_source_refs(fields: Sequence[Mapping[str, Any]]) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    for field in fields:
        for ref in field.get("source_refs", []):
            if not isinstance(ref, Mapping):
                continue
            artifact = ref.get("artifact")
            if not isinstance(artifact, str) or not artifact:
                continue
            if artifact not in seen:
                refs.append(artifact)
                seen.add(artifact)
            if len(refs) >= 6:
                return refs
    return refs


def _insert_before_heading(markdown: str, *, heading: str, insertion: str) -> str:
    marker = f"## {heading}"
    index = markdown.find(marker)
    if index == -1:
        raise DecisionWorkBriefEnrichmentInputError(
            f"brief Markdown was missing {heading} section"
        )
    prefix = markdown[:index].rstrip()
    suffix = markdown[index:].lstrip()
    return f"{prefix}\n\n{insertion}{suffix}"


def _insert_after_heading_intro(markdown: str, *, heading: str, insertion: str) -> str:
    pattern = re.compile(rf"(^## {re.escape(heading)}\n\n.*?\n\n)", re.MULTILINE | re.DOTALL)
    match = pattern.search(markdown)
    if not match:
        return _insert_before_heading(markdown, heading="Verification state", insertion=insertion)
    return markdown[: match.end()] + insertion + markdown[match.end() :]


def _remove_markdown_section(markdown: str, *, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\n.*?(?=^## |\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    return pattern.sub("", markdown).strip() + "\n"


def _remove_markdown_subsection(markdown: str, *, heading: str) -> str:
    pattern = re.compile(
        rf"^### {re.escape(heading)}\n.*?(?=^### |^## |\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    return pattern.sub("", markdown)


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
