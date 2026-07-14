"""Provider-free v2 prompt and response-custody contracts for R4.

The v1 complementary-reader module is frozen historical evidence.  This module
adds a prospective prompt contract without changing v1 packets, schemas,
compilers, or execution artifacts.  Meaning remains an LLM judgment; local code
only constructs prompts and inspects provider-envelope shape.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .r3_reasoning_exclusion import inspect_reasoning_exclusion
from .r4_complementary_readers import (
    RELATIONSHIP_PACKET_SCHEMA,
    UNCERTAINTY_PACKET_SCHEMA,
    R4ComplementaryReaderError,
    canonical_json_bytes,
    sha256_bytes,
)


SEMANTIC_DISTINCTION_PROMPT_CONTRACT = (
    "lolla.r4_semantic_distinction_prompt.v1"
)
R4_REASONING_CUSTODY_SCHEMA = "lolla.r4_reasoning_exclusion_inspection.v1"


def _prompt_result(system: str, user: str) -> dict[str, str]:
    return {
        "prompt_contract_version": SEMANTIC_DISTINCTION_PROMPT_CONTRACT,
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": sha256_bytes(system.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user.encode("utf-8")),
    }


def build_uncertainty_prompts_v2(packet: Mapping[str, Any]) -> dict[str, str]:
    """Build the prospective distinction-aware uncertainty prompt.

    The model receives complete source before the final task, compares the
    endpoint state with fallible prior interpretations, and is explicitly
    allowed to complete with zero.  No Python rule classifies a source passage.
    """

    if packet.get("schema_version") != UNCERTAINTY_PACKET_SCHEMA:
        raise R4ComplementaryReaderError("invalid uncertainty packet")
    source = packet["source"]
    prior = packet["prior_interpretation_context"]
    system = """<role>
You are a narrow complementary conversation-state reader. Interpret messy meaning across the complete conversation. Do not recommend action, select mental models, activate pressure, or score reasoning.
</role>

<authority>
The authoritative source outranks the fallible prior interpretations. Read the whole source and preserve speaker ownership and modal force. Source-supported inference is allowed; outside facts are forbidden. Do not infer resolution merely from turn order: compare the meanings of earlier and later evidence.
</authority>

<semantic_contract>
Review exactly two different surfaces.

UNRESOLVED MATTER: a material question, assumption, dependency, ownership gap, or tension that remains unanswered or unowned in the conversation's final state. It is not unresolved merely because an adopted action must still be executed, a signed condition must be satisfied, a written process exists, a safeguard remains active, or a risk was discussed earlier.

REOPEN CONDITION: specific later evidence, an event, or a dependency failure that would materially require reconsidering an otherwise current position. It is not a reopen condition merely because the current position already schedules a review, defines a benchmark, says pause or stop after a failure, prevents automatic renewal, or contains an operating requirement.

Before admitting a supported record, compare it with the current position and the complete source. Ask whether the same matter has already been resolved, assigned, operationalized, or deliberately converted into a precondition, process, safeguard, benchmark, or scheduled review. If yes and no distinct matter remains, return no record. If the source cannot establish whether the matter remains open, use ambiguous_review rather than forcing support.
</semantic_contract>

<contrastive_examples>
- "Proceed only after the amendment is signed" is normally an adopted condition precedent, not an unresolved matter.
- "Pause after a privacy failure and decide separately before renewal" is normally an existing safeguard, not a newly discovered reopen condition.
- "At six months, review results and whether unwelcome information travels upward" is normally an operationalized review, not a separate reopen condition.
- "We still need a boundary process" may be unresolved earlier, but is not still unresolved if the final position states that disputed cases follow the written boundary process.
- A pilot limited to one supported setting can still leave a distinct transfer or generalization question when the current position does not establish what wider settings justify.
- Temporary support can create a distinct reopen condition when continuation would otherwise hide an unresolved steady-state burden.
</contrastive_examples>

<output_rules>
It is correct to return no_supported_record_observed with an empty array. Use records_present only for at least one supported record. Use ambiguous_review only for one or more ambiguous records and no supported record. Cite exact source aliases. Return schema-valid JSON only.
</output_rules>"""
    user = (
        "<authoritative_source>\n"
        + canonical_json_bytes(source).decode("utf-8")
        + "\n</authoritative_source>\n\n<fallible_prior_interpretation_context>\n"
        + canonical_json_bytes(prior).decode("utf-8")
        + "\n</fallible_prior_interpretation_context>\n\n<task>\n"
        "Based on the information above, return exactly one review for "
        "unresolved_matter and one for reopen_condition, in either order. "
        "Return at most two records per review. Apply the semantic contract "
        "against the complete conversation endpoint, not isolated sentences. "
        "Preserve exact aliases, speaker ownership, and modal force. Do not "
        "judge advice quality or whether a human should trust an answer.\n"
        "</task>"
    )
    return _prompt_result(system, user)


def build_relationship_prompts_v2(packet: Mapping[str, Any]) -> dict[str, str]:
    """Build the prospective distinction-aware exact-ID relationship prompt."""

    if packet.get("schema_version") != RELATIONSHIP_PACKET_SCHEMA:
        raise R4ComplementaryReaderError("invalid relationship packet")
    system = """<role>
You are a narrow exact-ID relationship reader. Interpret relationships among unchanged provider-authored records and their source evidence. Do not create, merge, rewrite, rank, repair, or validate endpoint records.
</role>

<semantic_contract>
Return a relationship only when combining two or more exact records adds material, inspectable meaning that is not already contained in either endpoint. A useful relationship may constrain what a position can justify, connect a remaining uncertainty to the scope of a current position, or explain why distinct trajectories must be reconsidered together.

Co-occurrence is not a relationship. Shared evidence is not a relationship. The fact that one endpoint is labelled unresolved or reopen and another is a current position is not a relationship. Do not return a relationship that merely says the current position adopts a precondition, contains a safeguard, schedules a review, or uses a benchmark already stated by an endpoint. Do not paraphrase endpoints into relational language.

Endpoint records may be false positives. If the only available relationship depends on a record that its own source evidence shows was already incorporated or resolved, do not repair it and do not manufacture a relation; complete with zero and state the limitation globally. Use ambiguous_review only when a genuinely additive relation remains plausible but no stronger than ambiguous.
</semantic_contract>

<output_rules>
It is correct to return no_supported_record_observed with an empty array even when multiple records exist. Use only exact record IDs and exact evidence aliases from the packet. Return at most two relationships. Do not recommend action, select mental models, activate pressure, infer meaning from array order or ID text, or score quality. Return schema-valid JSON only.
</output_rules>"""
    user = (
        "<exact_id_record_packet>\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n</exact_id_record_packet>\n\n<task>\n"
        "Based on the packet above, return records_present only when at least "
        "one supported relationship adds meaning beyond its endpoints. Return "
        "ambiguous_review only when no relationship is stronger than ambiguous. "
        "Otherwise return no_supported_record_observed with an empty records "
        "array. Every non-zero relationship must name two to six different IDs "
        "from record_catalog and cite visible source aliases.\n</task>"
    )
    return _prompt_result(system, user)


def inspect_r4_reasoning_exclusion_v1(
    message: Mapping[str, object],
) -> dict[str, Any]:
    """Reuse the strict R3 content-shape validator for prospective R4 runners.

    The result contains locations and classifications only.  Provider values,
    reasoning text, summaries, encrypted payloads, and signatures are omitted.
    """

    inspection = inspect_reasoning_exclusion(message)
    return {
        "schema_version": R4_REASONING_CUSTODY_SCHEMA,
        "status": inspection.status,
        "exclusion_satisfied": inspection.exclusion_satisfied,
        "content_present": inspection.content_present,
        "metadata_only": inspection.metadata_only,
        "malformed": inspection.malformed,
        "detail_count": inspection.detail_count,
        "content_locations": list(inspection.content_locations),
        "metadata_locations": list(inspection.metadata_locations),
        "malformed_locations": list(inspection.malformed_locations),
        "provider_values_included": False,
        "historical_r4_result_reclassified": False,
    }
