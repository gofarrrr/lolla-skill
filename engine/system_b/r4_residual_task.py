"""Provider-free residual-task contract for the prospective R4 reader.

This additive module changes only the provider-visible semantic job identity.
Historical R4 prompt, schema, compiler, request, runner, and execution files stay
unchanged.  Local code owns declared surface mapping and structural custody; it
does not decide whether provider-authored prose is materially residual.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from typing import Any

from .r4_complementary_readers import (
    UNCERTAINTY_PACKET_SCHEMA,
    R4ComplementaryReaderError,
    canonical_json_bytes,
    compile_uncertainty_response_v1,
    sha256_bytes,
    uncertainty_response_schema_v1,
)


RESIDUAL_TASK_PROMPT_CONTRACT = "lolla.r4_residual_task_prompt.v1"
RESIDUAL_PROVIDER_SURFACES = (
    "residual_decision_gap",
    "residual_reconsideration_dependency",
)
RESIDUAL_SURFACE_TO_CANONICAL_ROLE = {
    "residual_decision_gap": "unresolved_matter",
    "residual_reconsideration_dependency": "reopen_condition",
}


def _prompt_result(system: str, user: str) -> dict[str, str]:
    return {
        "prompt_contract_version": RESIDUAL_TASK_PROMPT_CONTRACT,
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": sha256_bytes(system.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user.encode("utf-8")),
    }


def residual_response_schema_v1() -> dict[str, Any]:
    """Return the historical paired wire shape under residual-only wording."""

    schema = copy.deepcopy(uncertainty_response_schema_v1())
    schema["description"] = "Paired residual-discovery review."
    reviews = schema["properties"]["reviews"]
    reviews["description"] = "Exactly one review for each residual surface."
    review = reviews["items"]
    review["description"] = "One explicit residual-surface review."
    surface = review["properties"]["surface"]
    surface["enum"] = list(RESIDUAL_PROVIDER_SURFACES)
    surface["description"] = "The residual surface reviewed."
    review["properties"]["outcome"]["description"] = (
        "Present, quiet, or ambiguous result of this residual review."
    )
    records = review["properties"]["records"]
    records["description"] = "Zero to two candidates for this residual surface."
    record = records["items"]
    record["description"] = "One source-linked residual candidate."
    record["properties"]["support"]["description"] = (
        "Whether the source supports the residual or leaves it ambiguous."
    )
    record["properties"]["interpretation"]["description"] = (
        "Concise meaning of this residual without advice."
    )
    record["properties"]["evidence_ids"]["description"] = (
        "Exact source aliases that collectively establish the material dependency "
        "or question and why adopted machinery does not fully handle it."
    )
    record["properties"]["limitations"]["description"] = (
        "Residual uncertainty or scope limit; use an empty string if none."
    )
    return schema


def build_residual_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    """Build a minimal provider-visible residual-discovery prompt."""

    if packet.get("schema_version") != UNCERTAINTY_PACKET_SCHEMA:
        raise R4ComplementaryReaderError("invalid uncertainty packet")
    source = packet["source"]
    prior = packet["prior_interpretation_context"]
    system = """<role>
You are a narrow residual discovery reader. Your complete job is to find only material remainders that survive accounting for the current position's adopted decision machinery. Do not inventory everything pending. Do not give advice, select a graph, activate pressure, or score quality.
</role>

<authority>
The complete source is authoritative. Prior interpretations are fallible context, not source truth. Preserve speaker ownership and modal force. Source-supported inference is allowed; outside facts are forbidden. Omitted implementation detail is not affirmative evidence of absence.
</authority>

<residual_operation>
1. Account for what the current position already assigns, governs, safeguards, conditions, schedules, or deliberately defers for the present decision horizon.
2. Subtract that decision machinery and the pending work it already governs.
3. Emit only the materially distinct remainder affirmatively supported by the source.

RESIDUAL DECISION GAP: a materially distinct question, dependency, ownership gap, or tension that remains outside the adopted machinery after subtraction.

RESIDUAL RECONSIDERATION DEPENDENCY: materially distinct later evidence, an event, or a dependency failure outside the adopted machinery that would require reconsidering an otherwise current position.

Pending does not equal residual. Deferred does not equal unowned. A scheduled decision may leave its final outcome unselected while operationalizing the decision work. An existing threshold, benchmark, pause rule, fallback, exit, or scheduled review is not itself newly recovered pressure.
</residual_operation>

<evidence>
For every supported residual, cite exact source aliases that collectively establish both the material dependency or question and why the current position's adopted machinery does not fully handle it. Preserve the evidence for source-first review; do not rank evidence strength.
</evidence>

<examples>
- One-time installation funding plus unassigned recurring staffing and operating ownership can leave a residual decision gap.
- A supplier redesign governed by parallel proposals, milestones, fallback, criteria, and a fixed decision remains pending but is not residual merely because the final design is unselected.
- Independent evidence that defeats a premise of an otherwise current decision can be a residual reconsideration dependency when no adopted mechanism already governs that failure.
- A missing detail supports ambiguity only when a material residual is plausible and the source cannot establish whether it remains outside the adopted machinery.
</examples>

<output_rules>
Return no_supported_record_observed with an empty array when no distinct residual remains. Return ambiguous_review only for one or more ambiguous records and no supported record. Return records_present only for at least one supported residual. Cite exact source aliases and return schema-valid JSON only.
</output_rules>"""
    user = (
        "<authoritative_source>\n"
        + canonical_json_bytes(source).decode("utf-8")
        + "\n</authoritative_source>\n\n<fallible_prior_interpretation_context>\n"
        + canonical_json_bytes(prior).decode("utf-8")
        + "\n</fallible_prior_interpretation_context>\n\n<task>\n"
        "Perform residual accounting and subtraction over the complete source. "
        "Return exactly one review for residual_decision_gap and one for "
        "residual_reconsideration_dependency, in either order, with at most two "
        "records per review. Preserve exact aliases, speaker ownership, and modal "
        "force. Do not give advice, select a graph, or score quality.\n"
        "</task>"
    )
    return _prompt_result(system, user)


def map_residual_response_to_canonical_v1(
    response: Mapping[str, Any],
) -> dict[str, Any]:
    """Map only declared provider surface values to canonical internal roles."""

    mapped = copy.deepcopy(dict(response))
    reviews = mapped.get("reviews")
    if not isinstance(reviews, list):
        raise R4ComplementaryReaderError("residual reviews must be an array")
    for index, review in enumerate(reviews, 1):
        if not isinstance(review, dict):
            raise R4ComplementaryReaderError(
                f"residual review[{index}] must be an object"
            )
        surface = review.get("surface")
        canonical = RESIDUAL_SURFACE_TO_CANONICAL_ROLE.get(surface)
        if canonical is None:
            raise R4ComplementaryReaderError(
                "residual surface is invalid or undeclared"
            )
        review["surface"] = canonical
    return mapped


def compile_residual_response_v1(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    source_registry: Mapping[str, Any],
    planned_readers: Sequence[Mapping[str, Any]],
    artifact_path: str,
    artifact_bytes: bytes,
) -> dict[str, Any]:
    """Restore canonical roles, then delegate unchanged custody validation."""

    compiled = compile_uncertainty_response_v1(
        response=map_residual_response_to_canonical_v1(response),
        packet=packet,
        source_registry=source_registry,
        planned_readers=planned_readers,
        artifact_path=artifact_path,
        artifact_bytes=artifact_bytes,
    )
    compiled["boundary"] = {
        **compiled["boundary"],
        "provider_surface_values_mapped": True,
        "provider_surface_mapping": copy.deepcopy(
            RESIDUAL_SURFACE_TO_CANONICAL_ROLE
        ),
        "mapping_inspected_free_text": False,
        "model_record_prose_changed": False,
    }
    return compiled
