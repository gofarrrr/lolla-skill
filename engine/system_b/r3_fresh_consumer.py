"""Frozen R3 fresh-consumer pressure contract.

R3 is deliberately narrower than the live skill. It takes one already-frozen
simulated conversation, replays current R2 constitutional graph survival, and
asks one fresh model context to disposition every active pressure item. The
module contains no network behavior: it builds and validates the packet,
strict schema, request body, response, and source-review gate provider-free.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from .constitutional_graph_survival import (
    SCHEMA_VERSION as GRAPH_SURVIVAL_SCHEMA,
    validate_constitutional_graph_survival,
)


PACKET_SCHEMA = "lolla.r3_fresh_consumer_pressure_packet.v1"
BUNDLE_SCHEMA = "lolla.r3_fresh_consumer_pressure_bundle.v1"
RESPONSE_SCHEMA = "lolla.r3_fresh_consumer_pressure_response.v1"
REVIEW_SCHEMA = "lolla.r3_fresh_consumer_source_review.v1"
REVIEW_RESULT_SCHEMA = "lolla.r3_fresh_consumer_source_review_validation.v1"

MODEL = "google/gemini-3.1-flash-lite"
PROVIDER_ORDER = ("google-vertex/global",)
PROVIDER_ONLY = ("google-vertex",)
MAX_OUTPUT_TOKENS = 4000
MAX_PROVIDER_COST_USD = 0.01
MAX_PROVIDER_CALLS = 1
MAX_PROMPT_PRICE = 0.25
MAX_COMPLETION_PRICE = 1.50
SEED = 3101

ALLOWED_DISPOSITIONS = frozenset({"apply", "reject", "park"})
EFFECTS = frozenset(
    {
        "reframe",
        "new_condition",
        "new_alternative",
        "uncertainty_change",
        "reversal_rule",
        "reinforces_existing",
        "no_material_effect",
    }
)
REVIEW_DIMENSIONS = (
    "source_grounding",
    "disposition_quality",
    "non_forced_graph_contribution",
    "original_advice_preservation",
    "unsupported_claim_leakage",
    "private_over_absorption",
    "public_bloat_and_hedging",
    "exact_cost_and_failure_custody",
)


class R3FreshConsumerError(RuntimeError):
    """Raised when frozen R3 custody or response validation fails."""


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def value_sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def estimated_tokens(value: Any) -> int:
    return (len(canonical(value).encode("utf-8")) + 3) // 4


def _without(value: Mapping[str, Any], *fields: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key not in fields}


def _text(value: Any) -> str:
    return str(value or "").strip()


def source_turn_numbers(conversation: str) -> list[int]:
    turns = sorted(
        {
            int(value)
            for value in re.findall(
                r"(?m)^\[Turn (\d+)\] (?:USER|ASSISTANT):", conversation
            )
        }
    )
    if not turns:
        raise R3FreshConsumerError("authoritative conversation has no numbered turns")
    return turns


def final_assistant_answer(conversation: str) -> tuple[int, str]:
    matches = list(
        re.finditer(
            r"(?ms)^\[Turn (\d+)\] ASSISTANT:\n(.*?)(?=\n\[Turn \d+\] (?:USER|ASSISTANT):|\Z)",
            conversation,
        )
    )
    if not matches:
        raise R3FreshConsumerError("authoritative conversation has no assistant answer")
    match = matches[-1]
    return int(match.group(1)), match.group(2).strip()


def build_pressure_packet(
    *,
    case_id: str,
    conversation: str,
    constitutional_graph_survival: Mapping[str, Any],
    source_refs: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    if not _text(case_id):
        raise R3FreshConsumerError("case identity is required")
    validate_constitutional_graph_survival(constitutional_graph_survival)
    if constitutional_graph_survival.get("schema_version") != GRAPH_SURVIVAL_SCHEMA:
        raise R3FreshConsumerError("current constitutional graph portfolio is required")
    if constitutional_graph_survival.get("status") != "active":
        raise R3FreshConsumerError("R3 pressure case requires an active graph portfolio")
    active = constitutional_graph_survival.get("active_pressure_items")
    if not isinstance(active, list) or not active:
        raise R3FreshConsumerError("R3 pressure case has no active pressure")
    turns = source_turn_numbers(conversation)
    final_turn, original_answer = final_assistant_answer(conversation)
    packet: dict[str, Any] = {
        "schema_version": PACKET_SCHEMA,
        "case_id": case_id,
        "authoritative_conversation": conversation,
        "authoritative_conversation_sha256": text_sha256(conversation),
        "source_turn_numbers": turns,
        "preservation_material": {
            "original_final_assistant_turn": final_turn,
            "original_final_answer": original_answer,
            "original_final_answer_sha256": text_sha256(original_answer),
            "instruction": (
                "Preserve every source-grounded part that remains useful. Pressure is not "
                "permission to replace, lengthen, or hedge the answer."
            ),
        },
        "constitutional_graph_survival": dict(constitutional_graph_survival),
        "source_refs": [dict(item) for item in source_refs],
        "consumer_contract": {
            "fresh_context_required": True,
            "active_pressure_requires_apply_reject_or_park": True,
            "reserve_requires_current_disposition": False,
            "graph_recall_is_relevance_proof": False,
            "mental_models_are_case_evidence": False,
            "rejection_and_parking_are_valid": True,
            "public_use_required": False,
            "preserve_strong_original_reasoning": True,
            "unsupported_case_facts_allowed": False,
            "unsupported_quantitative_precision_allowed": False,
            "candidate_deletion_allowed": False,
        },
        "non_claims": [
            "fresh_context_is_not_independence_proof",
            "graph_recall_is_not_relevance_proof",
            "disposition_is_probabilistic",
            "reconsidered_answer_is_not_proven_better",
            "receipt_is_not_a_quality_certificate",
        ],
    }
    packet["packet_sha256"] = value_sha256(packet)
    validate_pressure_packet(packet)
    return packet


def validate_pressure_packet(packet: Mapping[str, Any]) -> None:
    if packet.get("schema_version") != PACKET_SCHEMA:
        raise R3FreshConsumerError("R3 pressure packet schema is invalid")
    observed_hash = _text(packet.get("packet_sha256"))
    if not observed_hash or observed_hash != value_sha256(_without(packet, "packet_sha256")):
        raise R3FreshConsumerError("R3 pressure packet hash is invalid")
    conversation = packet.get("authoritative_conversation")
    if not isinstance(conversation, str) or not conversation.strip():
        raise R3FreshConsumerError("R3 authoritative conversation is missing")
    if packet.get("authoritative_conversation_sha256") != text_sha256(conversation):
        raise R3FreshConsumerError("R3 authoritative conversation hash is invalid")
    if packet.get("source_turn_numbers") != source_turn_numbers(conversation):
        raise R3FreshConsumerError("R3 source-turn custody drifted")
    final_turn, original = final_assistant_answer(conversation)
    preservation = packet.get("preservation_material")
    if not isinstance(preservation, Mapping):
        raise R3FreshConsumerError("R3 preservation material is missing")
    if (
        preservation.get("original_final_assistant_turn") != final_turn
        or preservation.get("original_final_answer") != original
        or preservation.get("original_final_answer_sha256") != text_sha256(original)
    ):
        raise R3FreshConsumerError("R3 preservation material drifted from source")
    portfolio = packet.get("constitutional_graph_survival")
    if not isinstance(portfolio, Mapping):
        raise R3FreshConsumerError("R3 constitutional graph portfolio is missing")
    validate_constitutional_graph_survival(portfolio)


def _consumer_view(packet: Mapping[str, Any]) -> dict[str, Any]:
    validate_pressure_packet(packet)
    portfolio = packet["constitutional_graph_survival"]
    reserve = portfolio["reserve_custody"]
    return {
        "case_id": packet["case_id"],
        "authoritative_conversation": packet["authoritative_conversation"],
        "source_turn_numbers": packet["source_turn_numbers"],
        "preservation_material": packet["preservation_material"],
        "active_pressure_items": portfolio["active_pressure_items"],
        "reserve_notice": {
            "direct_capacity_reserve_model_ids": [
                item["model_id"] for item in reserve["direct_capacity_reserve"]
            ],
            "graph_edge_reserve_model_ids": [
                item["model_id"] for item in reserve["graph_edge_reserve"]
            ],
            "duplicate_input_count": len(reserve["duplicate_candidates"]),
            "malformed_input_count": len(reserve["malformed_candidates"]),
            "exact_reserve_location": (
                "persisted_packet.constitutional_graph_survival.reserve_custody"
            ),
            "portfolio_sha256": portfolio["portfolio_sha256"],
            "current_disposition_required": False,
            "semantic_rejection_performed": False,
        },
        "consumer_contract": packet["consumer_contract"],
        "packet_sha256": packet["packet_sha256"],
    }


def build_prompts(packet: Mapping[str, Any]) -> dict[str, str]:
    view = _consumer_view(packet)
    system = (
        "You are a fresh-context decision reasoner. Reconsider the complete supplied "
        "conversation using each active canonical pressure item as an intentionally noisy "
        "hypothesis. Graph recall is not relevance proof and a mental model is not case "
        "evidence. Preserve strong existing reasoning. Reject or park noise freely. Never "
        "invent facts, confidence, numerical precision, motives, or external conditions. "
        "Return only the strict JSON object requested by the response schema."
    )
    user = (
        "R3 FRESH-CONSUMER PRESSURE PACKET\n"
        + canonical(view)
        + "\n\nInspect every active pressure item exactly once and in packet order. First "
        "state its strongest plausible application and the condition that would have to "
        "hold. Then choose apply, reject, or park. Apply only when source turns support a "
        "concrete test, condition, alternative, uncertainty change, reversal rule, or useful "
        "private guardrail. Reject when the strongest application fails; name the failed "
        "condition and leave public/private effects empty. Park when evidence or timing is "
        "insufficient; name the exact reopening condition and leave effects empty. An apply "
        "must name a condition that could weaken or reopen it and must record either a visible "
        "effect or private guardrail. Cite only exact supplied turn numbers. Do not disposition "
        "reserve items.\n\nThen write one self-contained reconsidered answer. Include only earned "
        "friction, preserve useful original advice, and avoid exposing the model checklist. "
        "A valid result may keep the conclusion unchanged or publicly stand down. Finish with "
        "a concise factual change summary and an honest preservation classification."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": text_sha256(system),
        "user_prompt_sha256": text_sha256(user),
    }


def response_json_schema(packet: Mapping[str, Any]) -> dict[str, Any]:
    validate_pressure_packet(packet)
    active = packet["constitutional_graph_survival"]["active_pressure_items"]
    pressure_ids = [item["pressure_id"] for item in active]
    model_ids = [item["model_id"] for item in active]
    maximum_turn = max(packet["source_turn_numbers"])
    short_text = {"type": "string", "minLength": 0, "maxLength": 420}
    required_text = {"type": "string", "minLength": 1, "maxLength": 520}
    row = {
        "type": "object",
        "properties": {
            "pressure_id": {"type": "string", "enum": pressure_ids},
            "model_id": {"type": "string", "enum": model_ids},
            "disposition": {
                "type": "string",
                "enum": ["apply", "reject", "park"],
            },
            "source_turn_numbers": {
                "type": "array",
                "minItems": 1,
                "maxItems": 6,
                "items": {"type": "integer", "minimum": 1, "maximum": maximum_turn},
            },
            "effect": {"type": "string", "enum": sorted(EFFECTS)},
            "strongest_plausible_application": required_text,
            "attempted_application_condition": required_text,
            "why": required_text,
            "failed_condition": short_text,
            "reopen_condition": short_text,
            "visible_effect": short_text,
            "private_guardrail": short_text,
            "risk_if_forced": required_text,
            "risk_if_ignored": required_text,
        },
        "required": [
            "pressure_id",
            "model_id",
            "disposition",
            "source_turn_numbers",
            "effect",
            "strongest_plausible_application",
            "attempted_application_condition",
            "why",
            "failed_condition",
            "reopen_condition",
            "visible_effect",
            "private_guardrail",
            "risk_if_forced",
            "risk_if_ignored",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "candidate_dispositions": {
                "type": "array",
                "minItems": len(active),
                "maxItems": len(active),
                "items": row,
            },
            "reconsidered_answer": {
                "type": "string",
                "minLength": 1,
                "maxLength": 6000,
            },
            "change_summary": {
                "type": "string",
                "minLength": 1,
                "maxLength": 1200,
            },
            "original_answer_preservation": {
                "type": "string",
                "enum": ["preserved", "partially_changed", "replaced"],
            },
        },
        "required": [
            "candidate_dispositions",
            "reconsidered_answer",
            "change_summary",
            "original_answer_preservation",
        ],
        "additionalProperties": False,
    }


def build_request_body(packet: Mapping[str, Any]) -> dict[str, Any]:
    prompts = build_prompts(packet)
    schema = response_json_schema(packet)
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": prompts["user_prompt"]},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "lolla_r3_fresh_consumer_pressure",
                "strict": True,
                "schema": schema,
            },
        },
        "provider": {
            "order": list(PROVIDER_ORDER),
            "only": list(PROVIDER_ONLY),
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
            "max_price": {
                "prompt": MAX_PROMPT_PRICE,
                "completion": MAX_COMPLETION_PRICE,
            },
        },
        "seed": SEED,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "reasoning": {"effort": "low", "exclude": True},
        "stream": False,
    }


def maximum_estimated_call_cost_usd(body: Mapping[str, Any]) -> float:
    input_tokens = estimated_tokens(_without(body, "max_tokens"))
    output_tokens = int(body.get("max_tokens", 0) or 0)
    return round(
        input_tokens * MAX_PROMPT_PRICE / 1_000_000
        + output_tokens * MAX_COMPLETION_PRICE / 1_000_000,
        9,
    )


def build_pressure_bundle(
    *,
    case_id: str,
    conversation: str,
    constitutional_graph_survival: Mapping[str, Any],
    source_refs: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    packet = build_pressure_packet(
        case_id=case_id,
        conversation=conversation,
        constitutional_graph_survival=constitutional_graph_survival,
        source_refs=source_refs,
    )
    prompts = build_prompts(packet)
    schema = response_json_schema(packet)
    body = build_request_body(packet)
    maximum_cost = maximum_estimated_call_cost_usd(body)
    if maximum_cost > MAX_PROVIDER_COST_USD:
        raise R3FreshConsumerError("R3 request exceeds the frozen $0.01 envelope")
    bundle: dict[str, Any] = {
        "schema_version": BUNDLE_SCHEMA,
        "status": "provider_free_preflight_ready",
        "case_id": case_id,
        "packet": packet,
        "prompts": prompts,
        "response_schema": schema,
        "request_body": body,
        "request_contract": {
            "provider": "openrouter",
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "requested_model": MODEL,
            "provider_order": list(PROVIDER_ORDER),
            "provider_only": list(PROVIDER_ONLY),
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
            "zdr_claimed": False,
            "wire_mode": "strict_json_schema",
            "reasoning_effort": "low",
            "reasoning_content_excluded": True,
            "seed": SEED,
            "maximum_output_tokens": MAX_OUTPUT_TOKENS,
            "maximum_provider_calls": MAX_PROVIDER_CALLS,
            "maximum_provider_reported_cost_usd": MAX_PROVIDER_COST_USD,
            "maximum_estimated_call_cost_usd": maximum_cost,
            "automatic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
            "parallel_calls": False,
        },
        "hashes": {
            "system_prompt_sha256": prompts["system_prompt_sha256"],
            "user_prompt_sha256": prompts["user_prompt_sha256"],
            "response_schema_sha256": value_sha256(schema),
            "request_body_sha256": value_sha256(body),
            "constitutional_graph_portfolio_sha256": constitutional_graph_survival[
                "portfolio_sha256"
            ],
        },
        "next_call_authorized": False,
        "provider_calls_made": 0,
    }
    bundle["bundle_sha256"] = value_sha256(bundle)
    validate_pressure_bundle(bundle)
    return bundle


def validate_pressure_bundle(bundle: Mapping[str, Any]) -> None:
    if bundle.get("schema_version") != BUNDLE_SCHEMA:
        raise R3FreshConsumerError("R3 pressure bundle schema is invalid")
    observed = _text(bundle.get("bundle_sha256"))
    if not observed or observed != value_sha256(_without(bundle, "bundle_sha256")):
        raise R3FreshConsumerError("R3 pressure bundle hash is invalid")
    packet = bundle.get("packet")
    if not isinstance(packet, Mapping):
        raise R3FreshConsumerError("R3 pressure bundle lacks its packet")
    validate_pressure_packet(packet)
    prompts = build_prompts(packet)
    schema = response_json_schema(packet)
    body = build_request_body(packet)
    if bundle.get("prompts") != prompts or bundle.get("response_schema") != schema:
        raise R3FreshConsumerError("R3 prompts or schema drifted")
    if bundle.get("request_body") != body:
        raise R3FreshConsumerError("R3 request body drifted")
    hashes = bundle.get("hashes")
    if not isinstance(hashes, Mapping) or hashes != {
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": value_sha256(schema),
        "request_body_sha256": value_sha256(body),
        "constitutional_graph_portfolio_sha256": packet[
            "constitutional_graph_survival"
        ]["portfolio_sha256"],
    }:
        raise R3FreshConsumerError("R3 bundle hash custody is invalid")
    contract = bundle.get("request_contract")
    if not isinstance(contract, Mapping):
        raise R3FreshConsumerError("R3 request contract is missing")
    required = {
        "maximum_provider_calls": MAX_PROVIDER_CALLS,
        "maximum_provider_reported_cost_usd": MAX_PROVIDER_COST_USD,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "wire_mode": "strict_json_schema",
        "zdr_claimed": False,
    }
    for field, expected in required.items():
        if contract.get(field) != expected:
            raise R3FreshConsumerError(f"R3 request contract drifted: {field}")
    if maximum_estimated_call_cost_usd(body) > MAX_PROVIDER_COST_USD:
        raise R3FreshConsumerError("R3 request exceeds the frozen cost envelope")


def compile_pressure_response(
    *, response: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    validate_pressure_packet(packet)
    required_top = {
        "candidate_dispositions",
        "reconsidered_answer",
        "change_summary",
        "original_answer_preservation",
    }
    if set(response) != required_top:
        raise R3FreshConsumerError("R3 response envelope is invalid")
    active = packet["constitutional_graph_survival"]["active_pressure_items"]
    observed = response.get("candidate_dispositions")
    if not isinstance(observed, list) or len(observed) != len(active):
        raise R3FreshConsumerError("R3 response does not cover every active pressure")
    row_fields = {
        "pressure_id",
        "model_id",
        "disposition",
        "source_turn_numbers",
        "effect",
        "strongest_plausible_application",
        "attempted_application_condition",
        "why",
        "failed_condition",
        "reopen_condition",
        "visible_effect",
        "private_guardrail",
        "risk_if_forced",
        "risk_if_ignored",
    }
    valid_turns = set(packet["source_turn_numbers"])
    disposition_counts: dict[str, int] = {}
    compiled: list[dict[str, Any]] = []
    for index, (row, expected) in enumerate(zip(observed, active)):
        prefix = f"candidate_dispositions[{index}]"
        if not isinstance(row, Mapping) or set(row) != row_fields:
            raise R3FreshConsumerError(f"{prefix} shape is invalid")
        if (
            row.get("pressure_id") != expected["pressure_id"]
            or row.get("model_id") != expected["model_id"]
        ):
            raise R3FreshConsumerError(f"{prefix} identity or packet order drifted")
        disposition = _text(row.get("disposition"))
        effect = _text(row.get("effect"))
        if disposition not in ALLOWED_DISPOSITIONS or effect not in EFFECTS:
            raise R3FreshConsumerError(f"{prefix} disposition or effect is invalid")
        turns = row.get("source_turn_numbers")
        if (
            not isinstance(turns, list)
            or not turns
            or len(turns) != len(set(turns))
            or set(turns) - valid_turns
        ):
            raise R3FreshConsumerError(f"{prefix} source-turn custody is invalid")
        for field in (
            "strongest_plausible_application",
            "attempted_application_condition",
            "why",
            "risk_if_forced",
            "risk_if_ignored",
        ):
            if not _text(row.get(field)):
                raise R3FreshConsumerError(f"{prefix}.{field} is required")
        failed = _text(row.get("failed_condition"))
        reopen = _text(row.get("reopen_condition"))
        visible = _text(row.get("visible_effect"))
        private = _text(row.get("private_guardrail"))
        if disposition == "apply":
            if effect == "no_material_effect" or not (visible or private) or not reopen:
                raise R3FreshConsumerError(
                    f"{prefix} apply requires a material effect, effect custody, and falsifier"
                )
            if failed:
                raise R3FreshConsumerError(f"{prefix} apply cannot claim failed condition")
        elif disposition == "reject":
            if effect != "no_material_effect" or not failed or visible or private:
                raise R3FreshConsumerError(
                    f"{prefix} reject requires failed condition and no claimed effect"
                )
        elif disposition == "park":
            if effect != "no_material_effect" or not reopen or visible or private:
                raise R3FreshConsumerError(
                    f"{prefix} park requires reopen condition and no claimed effect"
                )
            if failed:
                raise R3FreshConsumerError(f"{prefix} park cannot claim failed condition")
        disposition_counts[disposition] = disposition_counts.get(disposition, 0) + 1
        compiled.append(dict(row))
    for field in ("reconsidered_answer", "change_summary"):
        if not _text(response.get(field)):
            raise R3FreshConsumerError(f"R3 response {field} is empty")
    if response.get("original_answer_preservation") not in {
        "preserved",
        "partially_changed",
        "replaced",
    }:
        raise R3FreshConsumerError("R3 original-answer preservation value is invalid")
    return {
        "schema_version": RESPONSE_SCHEMA,
        "case_id": packet["case_id"],
        "source_packet_sha256": packet["packet_sha256"],
        "candidate_dispositions": compiled,
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "reconsidered_answer": response["reconsidered_answer"],
        "change_summary": response["change_summary"],
        "original_answer_preservation": response["original_answer_preservation"],
        "all_active_candidates_accounted_for": True,
        "runtime_effect": "none",
        "non_claims": [
            "mechanically_valid_is_not_semantically_grounded",
            "reconsidered_answer_is_not_proven_better",
            "source_review_is_still_required",
        ],
    }


def build_source_review_template(
    *, bundle: Mapping[str, Any], call_result_sha256: str
) -> dict[str, Any]:
    validate_pressure_bundle(bundle)
    active = bundle["packet"]["constitutional_graph_survival"]["active_pressure_items"]
    return {
        "schema_version": REVIEW_SCHEMA,
        "status": "completed",
        "case_id": bundle["case_id"],
        "bundle_sha256": bundle["bundle_sha256"],
        "call_result_sha256": call_result_sha256,
        "reviewer_kind": "codex_source_first_no_provider_call",
        "dimensions": [
            {
                "dimension": dimension,
                "verdict": "",
                "why": "",
                "source_turn_numbers": [],
                "pressure_ids": [],
                "response_evidence": "",
            }
            for dimension in REVIEW_DIMENSIONS
        ],
        "value_signal": {
            "kind": "",
            "pressure_ids": [],
            "source_turn_numbers": [],
            "why": "",
        },
        "pressure_case_decision": "",
        "quiet_control_authorized": False,
        "scalar_quality_score": None,
        "notes": [
            f"Review all {len(active)} active dispositions source-first; do not reward fluency."
        ],
    }


def validate_source_review(
    review: Mapping[str, Any], *, bundle: Mapping[str, Any], call_result_sha256: str
) -> dict[str, Any]:
    validate_pressure_bundle(bundle)
    errors: list[str] = []
    required_top = {
        "schema_version",
        "status",
        "case_id",
        "bundle_sha256",
        "call_result_sha256",
        "reviewer_kind",
        "dimensions",
        "value_signal",
        "pressure_case_decision",
        "quiet_control_authorized",
        "scalar_quality_score",
        "notes",
    }
    if set(review) != required_top:
        errors.append("review top-level fields are invalid")
    if review.get("schema_version") != REVIEW_SCHEMA or review.get("status") != "completed":
        errors.append("review schema or status is invalid")
    if (
        review.get("case_id") != bundle.get("case_id")
        or review.get("bundle_sha256") != bundle.get("bundle_sha256")
        or review.get("call_result_sha256") != call_result_sha256
    ):
        errors.append("review source identity custody is invalid")
    if review.get("reviewer_kind") != "codex_source_first_no_provider_call":
        errors.append("reviewer kind is invalid")
    if review.get("scalar_quality_score") is not None:
        errors.append("scalar quality score is prohibited")
    valid_turns = set(bundle["packet"]["source_turn_numbers"])
    active = bundle["packet"]["constitutional_graph_survival"]["active_pressure_items"]
    valid_pressure_ids = {item["pressure_id"] for item in active}
    dimensions = review.get("dimensions")
    observed_dimensions: list[str] = []
    verdicts: dict[str, str] = {}
    if not isinstance(dimensions, list) or len(dimensions) != len(REVIEW_DIMENSIONS):
        errors.append("review must contain every dimension exactly once")
        dimensions = []
    dimension_fields = {
        "dimension",
        "verdict",
        "why",
        "source_turn_numbers",
        "pressure_ids",
        "response_evidence",
    }
    for index, item in enumerate(dimensions):
        if not isinstance(item, Mapping) or set(item) != dimension_fields:
            errors.append(f"dimensions[{index}] shape is invalid")
            continue
        dimension = _text(item.get("dimension"))
        verdict = _text(item.get("verdict"))
        observed_dimensions.append(dimension)
        verdicts[dimension] = verdict
        if verdict not in {"pass", "fail", "uncertain"}:
            errors.append(f"dimensions[{index}].verdict is invalid")
        if not _text(item.get("why")) or not _text(item.get("response_evidence")):
            errors.append(f"dimensions[{index}] lacks review evidence")
        turns = item.get("source_turn_numbers")
        pressure_ids = item.get("pressure_ids")
        if not isinstance(turns, list) or set(turns) - valid_turns:
            errors.append(f"dimensions[{index}] has invalid source turns")
        if not isinstance(pressure_ids, list) or set(pressure_ids) - valid_pressure_ids:
            errors.append(f"dimensions[{index}] has invalid pressure IDs")
    if observed_dimensions != list(REVIEW_DIMENSIONS):
        errors.append("review dimension order or coverage is invalid")
    value = review.get("value_signal")
    if not isinstance(value, Mapping) or set(value) != {
        "kind",
        "pressure_ids",
        "source_turn_numbers",
        "why",
    }:
        errors.append("value signal shape is invalid")
        value = {}
    kind = _text(value.get("kind"))
    if kind not in {"applied_contribution", "valuable_rejection", "none"}:
        errors.append("value signal kind is invalid")
    value_pressure = value.get("pressure_ids")
    value_turns = value.get("source_turn_numbers")
    if (
        not isinstance(value_pressure, list)
        or set(value_pressure) - valid_pressure_ids
        or not isinstance(value_turns, list)
        or set(value_turns) - valid_turns
        or not _text(value.get("why"))
    ):
        errors.append("value signal evidence is invalid")
    if kind != "none" and (not value_pressure or not value_turns):
        errors.append("positive value signal requires pressure and source evidence")
    decision = review.get("pressure_case_decision")
    quiet = review.get("quiet_control_authorized")
    if decision not in {"pass_authorize_quiet_control", "fail_preserve_and_stop"}:
        errors.append("pressure-case decision is invalid")
    expected_pass = (
        not errors
        and all(verdicts.get(name) == "pass" for name in REVIEW_DIMENSIONS)
        and kind in {"applied_contribution", "valuable_rejection"}
    )
    if expected_pass and (decision != "pass_authorize_quiet_control" or quiet is not True):
        errors.append("passing pressure case must explicitly authorize the quiet control")
    if not expected_pass and (decision != "fail_preserve_and_stop" or quiet is not False):
        errors.append("nonpassing pressure case must preserve failure and stop")
    return {
        "schema_version": REVIEW_RESULT_SCHEMA,
        "status": "valid" if not errors else "invalid",
        "pressure_case_passed": expected_pass and not errors,
        "quiet_control_authorized": expected_pass and not errors,
        "dimension_verdicts": verdicts,
        "value_signal_kind": kind,
        "errors": errors,
    }
