"""Provider-free R3 final-consumer task-shape counterfactuals.

This module does not change the live R3 path and contains no network behavior.
It compares the frozen one-pass projection with two prospective alternatives:

* one pass with disposition and effect collapsed into one controlled outcome;
* the same disposition contract followed by a separate answer-synthesis pass.

The combined outcome remains a model judgment. Deterministic code only maps an
explicit controlled label back to the canonical disposition/effect pair and
validates custody. It never decides whether a pressure item applies.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping
from typing import Any

from .r3_fresh_consumer import (
    MAX_COMPLETION_PRICE,
    MAX_PROMPT_PRICE,
    build_prompts,
    canonical,
    compile_pressure_response,
    estimated_tokens,
    text_sha256,
    validate_pressure_packet,
    value_sha256,
)
from .r3_google_schema_projection import (
    BOUNDARY_TEXT_MAX,
    CHANGE_SUMMARY_MAX,
    EFFECT_TEXT_MAX,
    RECONSIDERED_ANSWER_MAX,
    REQUIRED_ROW_TEXT_MAX,
    lint_google_documented_schema_subset,
    schema_metrics,
)


COUNTERFACTUAL_SCHEMA = "lolla.r3_task_shape_counterfactual.v1"
DISPOSITION_LEDGER_SCHEMA = "lolla.r3_collapsed_outcome_ledger.v1"
SYNTHESIS_PACKET_SCHEMA = "lolla.r3_separated_synthesis_packet.v1"

MATERIAL_EFFECTS = (
    "new_alternative",
    "new_condition",
    "reframe",
    "reinforces_existing",
    "reversal_rule",
    "uncertainty_change",
)
OUTCOME_MAP: dict[str, tuple[str, str]] = {
    **{f"apply_{effect}": ("apply", effect) for effect in MATERIAL_EFFECTS},
    "reject": ("reject", "no_material_effect"),
    "park": ("park", "no_material_effect"),
}
ROW_FIELDS = (
    "pressure_id",
    "outcome",
    "source_turn_numbers",
    "strongest_plausible_application",
    "attempted_application_condition",
    "why",
    "disposition_boundary",
    "visible_effect",
    "private_guardrail",
)
SYNTHESIS_FIELDS = (
    "reconsidered_answer",
    "change_summary",
    "original_answer_preservation",
)

ONE_PASS_MAX_OUTPUT_TOKENS = 4000
DISPOSITION_STAGE_MAX_OUTPUT_TOKENS = 3200
SYNTHESIS_STAGE_MAX_OUTPUT_TOKENS = 1400


class R3TaskShapeError(RuntimeError):
    """Raised when a task-shape counterfactual loses custody."""


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bounded_text(
    value: Any, *, field: str, maximum: int, allow_empty: bool
) -> str:
    if not isinstance(value, str):
        raise R3TaskShapeError(f"{field} must be text")
    if not allow_empty and not value.strip():
        raise R3TaskShapeError(f"{field} is required")
    if len(value) > maximum:
        raise R3TaskShapeError(f"{field} exceeds local length boundary")
    return value


def _row_schema(packet: Mapping[str, Any]) -> dict[str, Any]:
    maximum_turn = max(packet["source_turn_numbers"])
    return {
        "type": "object",
        "properties": {
            "pressure_id": {
                "type": "string",
                "description": "Exact pressure_id from the matching packet row, in order.",
            },
            "outcome": {
                "type": "string",
                "enum": list(OUTCOME_MAP),
                "description": (
                    "One combined disposition/effect judgment. Apply labels carry the "
                    "material effect; reject and park carry no current material effect."
                ),
            },
            "source_turn_numbers": {
                "type": "array",
                "minItems": 1,
                "maxItems": 6,
                "items": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": maximum_turn,
                },
                "description": "Exact supplied turns supporting this judgment.",
            },
            "strongest_plausible_application": {
                "type": "string",
                "description": "Strongest good-faith source-grounded use before judgment.",
            },
            "attempted_application_condition": {
                "type": "string",
                "description": "Condition required for the application to be sound.",
            },
            "why": {
                "type": "string",
                "description": "Source-grounded reason for the selected outcome.",
            },
            "disposition_boundary": {
                "type": "string",
                "description": (
                    "Failed condition for reject; reopen or falsifier for park/apply."
                ),
            },
            "visible_effect": {
                "type": "string",
                "description": "Public effect for apply; otherwise empty.",
            },
            "private_guardrail": {
                "type": "string",
                "description": "Private guardrail for apply; otherwise empty.",
            },
        },
        "required": list(ROW_FIELDS),
        "additionalProperties": False,
    }


def collapsed_disposition_schema(packet: Mapping[str, Any]) -> dict[str, Any]:
    validate_pressure_packet(packet)
    active = packet["constitutional_graph_survival"]["active_pressure_items"]
    schema = {
        "type": "object",
        "properties": {
            "candidate_dispositions": {
                "type": "array",
                "minItems": len(active),
                "maxItems": len(active),
                "items": _row_schema(packet),
                "description": "One outcome for every active pressure, in packet order.",
            }
        },
        "required": ["candidate_dispositions"],
        "additionalProperties": False,
    }
    if lint_google_documented_schema_subset(schema)["status"] != "pass_documented_subset":
        raise R3TaskShapeError("collapsed disposition schema escaped documented subset")
    return schema


def collapsed_one_pass_schema(packet: Mapping[str, Any]) -> dict[str, Any]:
    validate_pressure_packet(packet)
    disposition = collapsed_disposition_schema(packet)
    properties = copy.deepcopy(disposition["properties"])
    properties.update(
        {
            "reconsidered_answer": {
                "type": "string",
                "description": "Self-contained answer containing only earned friction.",
            },
            "change_summary": {
                "type": "string",
                "description": "Concise factual account of change or stand-down.",
            },
            "original_answer_preservation": {
                "type": "string",
                "enum": ["preserved", "partially_changed", "replaced"],
                "description": "Classification of useful original-answer preservation.",
            },
        }
    )
    schema = {
        "type": "object",
        "properties": properties,
        "required": ["candidate_dispositions", *SYNTHESIS_FIELDS],
        "additionalProperties": False,
    }
    if lint_google_documented_schema_subset(schema)["status"] != "pass_documented_subset":
        raise R3TaskShapeError("collapsed one-pass schema escaped documented subset")
    return schema


def synthesis_response_schema() -> dict[str, Any]:
    schema = {
        "type": "object",
        "properties": {
            "reconsidered_answer": {
                "type": "string",
                "description": "Self-contained answer containing only earned friction.",
            },
            "change_summary": {
                "type": "string",
                "description": "Concise factual account of change or stand-down.",
            },
            "original_answer_preservation": {
                "type": "string",
                "enum": ["preserved", "partially_changed", "replaced"],
                "description": "Classification of useful original-answer preservation.",
            },
        },
        "required": list(SYNTHESIS_FIELDS),
        "additionalProperties": False,
    }
    if lint_google_documented_schema_subset(schema)["status"] != "pass_documented_subset":
        raise R3TaskShapeError("synthesis schema escaped documented subset")
    return schema


def _outcome_instruction() -> str:
    return (
        "\n\nCOUNTERFACTUAL OUTCOME PROJECTION: Express disposition and effect once in "
        "the outcome field. Use reject or park only when there is no current material "
        "effect and leave visible_effect/private_guardrail empty. Use apply_<effect> "
        "only with public or private effect custody. The controlled label is your "
        "semantic judgment; deterministic code only maps it back to the canonical pair."
    )


def collapsed_one_pass_prompts(packet: Mapping[str, Any]) -> dict[str, str]:
    base = build_prompts(packet)
    user = base["user_prompt"] + _outcome_instruction()
    return {
        "system_prompt": base["system_prompt"],
        "user_prompt": user,
        "system_prompt_sha256": base["system_prompt_sha256"],
        "user_prompt_sha256": text_sha256(user),
    }


def disposition_stage_prompts(packet: Mapping[str, Any]) -> dict[str, str]:
    base = build_prompts(packet)
    marker = "\n\nThen write one self-contained reconsidered answer."
    before, found, _after = base["user_prompt"].partition(marker)
    if not found:
        raise R3TaskShapeError("frozen R3 prompt no longer exposes synthesis boundary")
    system = (
        "You are a fresh-context pressure disposition reasoner. Inspect every supplied "
        "canonical pressure as intentional noise. Graph recall is not relevance proof. "
        "Apply, reject, or park freely from the complete conversation. Never draft the "
        "final answer and never invent facts. Return only the requested JSON object."
    )
    user = before + _outcome_instruction() + (
        "\n\nStop after the complete disposition ledger. Do not draft, summarize, or "
        "classify preservation of the final answer."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": text_sha256(system),
        "user_prompt_sha256": text_sha256(user),
    }


def _request_body(
    *, base_body: Mapping[str, Any], prompts: Mapping[str, str], schema: Mapping[str, Any],
    name: str, maximum_output_tokens: int
) -> dict[str, Any]:
    body = copy.deepcopy(base_body)
    body["messages"] = [
        {"role": "system", "content": prompts["system_prompt"]},
        {"role": "user", "content": prompts["user_prompt"]},
    ]
    body["response_format"] = {
        "type": "json_schema",
        "json_schema": {"name": name, "strict": True, "schema": copy.deepcopy(schema)},
    }
    body["max_tokens"] = maximum_output_tokens
    return body


def collapsed_one_pass_request_body(
    *, base_body: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    return _request_body(
        base_body=base_body,
        prompts=collapsed_one_pass_prompts(packet),
        schema=collapsed_one_pass_schema(packet),
        name="lolla_r3_collapsed_outcome_one_pass",
        maximum_output_tokens=ONE_PASS_MAX_OUTPUT_TOKENS,
    )


def disposition_stage_request_body(
    *, base_body: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    return _request_body(
        base_body=base_body,
        prompts=disposition_stage_prompts(packet),
        schema=collapsed_disposition_schema(packet),
        name="lolla_r3_collapsed_outcome_disposition_stage",
        maximum_output_tokens=DISPOSITION_STAGE_MAX_OUTPUT_TOKENS,
    )


def _compile_rows(
    *, rows: Any, packet: Mapping[str, Any]
) -> list[dict[str, Any]]:
    validate_pressure_packet(packet)
    active = packet["constitutional_graph_survival"]["active_pressure_items"]
    if not isinstance(rows, list) or len(rows) != len(active):
        raise R3TaskShapeError("collapsed response lacks exact active coverage")
    valid_turns = set(packet["source_turn_numbers"])
    compiled: list[dict[str, Any]] = []
    for index, (row, expected) in enumerate(zip(rows, active)):
        prefix = f"candidate_dispositions[{index}]"
        if not isinstance(row, Mapping) or set(row) != set(ROW_FIELDS):
            raise R3TaskShapeError(f"{prefix} shape is invalid")
        if row.get("pressure_id") != expected["pressure_id"]:
            raise R3TaskShapeError(f"{prefix} pressure identity or order drifted")
        outcome = row.get("outcome")
        if outcome not in OUTCOME_MAP:
            raise R3TaskShapeError(f"{prefix} outcome is invalid")
        disposition, effect = OUTCOME_MAP[str(outcome)]
        turns = row.get("source_turn_numbers")
        if (
            not isinstance(turns, list)
            or not turns
            or len(turns) > 6
            or any(not isinstance(turn, int) or isinstance(turn, bool) for turn in turns)
            or len(turns) != len(set(turns))
            or set(turns) - valid_turns
        ):
            raise R3TaskShapeError(f"{prefix} source-turn custody is invalid")
        strongest = _bounded_text(
            row.get("strongest_plausible_application"),
            field=f"{prefix}.strongest_plausible_application",
            maximum=REQUIRED_ROW_TEXT_MAX,
            allow_empty=False,
        )
        attempted = _bounded_text(
            row.get("attempted_application_condition"),
            field=f"{prefix}.attempted_application_condition",
            maximum=REQUIRED_ROW_TEXT_MAX,
            allow_empty=False,
        )
        why = _bounded_text(
            row.get("why"),
            field=f"{prefix}.why",
            maximum=REQUIRED_ROW_TEXT_MAX,
            allow_empty=False,
        )
        boundary = _bounded_text(
            row.get("disposition_boundary"),
            field=f"{prefix}.disposition_boundary",
            maximum=BOUNDARY_TEXT_MAX,
            allow_empty=False,
        )
        visible = _bounded_text(
            row.get("visible_effect"),
            field=f"{prefix}.visible_effect",
            maximum=EFFECT_TEXT_MAX,
            allow_empty=True,
        )
        private = _bounded_text(
            row.get("private_guardrail"),
            field=f"{prefix}.private_guardrail",
            maximum=EFFECT_TEXT_MAX,
            allow_empty=True,
        )
        if disposition == "apply":
            if not (visible.strip() or private.strip()):
                raise R3TaskShapeError(f"{prefix} apply lacks effect custody")
            failed_condition = ""
            reopen_condition = boundary
        elif visible.strip() or private.strip():
            raise R3TaskShapeError(f"{prefix} {disposition} claims effect custody")
        elif disposition == "reject":
            failed_condition = boundary
            reopen_condition = ""
        else:
            failed_condition = ""
            reopen_condition = boundary
        compiled.append(
            {
                "pressure_id": expected["pressure_id"],
                "model_id": expected["model_id"],
                "disposition": disposition,
                "source_turn_numbers": list(turns),
                "effect": effect,
                "strongest_plausible_application": strongest,
                "attempted_application_condition": attempted,
                "why": why,
                "failed_condition": failed_condition,
                "reopen_condition": reopen_condition,
                "visible_effect": visible,
                "private_guardrail": private,
                "risk_if_forced": expected["force_boundary"],
                "risk_if_ignored": expected["ignore_boundary"],
            }
        )
    return compiled


def compile_collapsed_one_pass_response(
    *, response: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    required = {"candidate_dispositions", *SYNTHESIS_FIELDS}
    if set(response) != required:
        raise R3TaskShapeError("collapsed one-pass response envelope is invalid")
    canonical_rows = _compile_rows(
        rows=response.get("candidate_dispositions"), packet=packet
    )
    canonical_response = {
        "candidate_dispositions": canonical_rows,
        "reconsidered_answer": _bounded_text(
            response.get("reconsidered_answer"),
            field="reconsidered_answer",
            maximum=RECONSIDERED_ANSWER_MAX,
            allow_empty=False,
        ),
        "change_summary": _bounded_text(
            response.get("change_summary"),
            field="change_summary",
            maximum=CHANGE_SUMMARY_MAX,
            allow_empty=False,
        ),
        "original_answer_preservation": response.get("original_answer_preservation"),
    }
    result = compile_pressure_response(response=canonical_response, packet=packet)
    result["counterfactual_projection"] = {
        "schema_version": COUNTERFACTUAL_SCHEMA,
        "wire_outcome_mapped_deterministically": True,
        "semantic_applicability_inferred_by_code": False,
        "candidate_deletion_allowed": False,
    }
    return result


def compile_disposition_stage_response(
    *, response: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    if set(response) != {"candidate_dispositions"}:
        raise R3TaskShapeError("disposition-stage response envelope is invalid")
    rows = _compile_rows(rows=response.get("candidate_dispositions"), packet=packet)
    ledger: dict[str, Any] = {
        "schema_version": DISPOSITION_LEDGER_SCHEMA,
        "case_id": packet["case_id"],
        "source_packet_sha256": packet["packet_sha256"],
        "candidate_dispositions": rows,
        "candidate_count": len(rows),
        "all_active_candidates_accounted_for": True,
        "semantic_applicability_inferred_by_code": False,
    }
    ledger["ledger_sha256"] = value_sha256(ledger)
    return ledger


def validate_disposition_ledger(
    ledger: Mapping[str, Any], *, packet: Mapping[str, Any]
) -> None:
    if ledger.get("schema_version") != DISPOSITION_LEDGER_SCHEMA:
        raise R3TaskShapeError("disposition ledger schema is invalid")
    observed = ledger.get("ledger_sha256")
    without = {key: value for key, value in ledger.items() if key != "ledger_sha256"}
    if observed != value_sha256(without):
        raise R3TaskShapeError("disposition ledger hash drifted")
    if (
        ledger.get("case_id") != packet["case_id"]
        or ledger.get("source_packet_sha256") != packet["packet_sha256"]
    ):
        raise R3TaskShapeError("disposition ledger source custody drifted")
    active = packet["constitutional_graph_survival"]["active_pressure_items"]
    rows = ledger.get("candidate_dispositions")
    if not isinstance(rows, list) or len(rows) != len(active):
        raise R3TaskShapeError("disposition ledger active coverage drifted")
    for row, expected in zip(rows, active):
        if not isinstance(row, Mapping) or (
            row.get("pressure_id") != expected["pressure_id"]
            or row.get("model_id") != expected["model_id"]
        ):
            raise R3TaskShapeError("disposition ledger identity drifted")


def build_synthesis_packet(
    *, packet: Mapping[str, Any], ledger: Mapping[str, Any]
) -> dict[str, Any]:
    validate_pressure_packet(packet)
    validate_disposition_ledger(ledger, packet=packet)
    value: dict[str, Any] = {
        "schema_version": SYNTHESIS_PACKET_SCHEMA,
        "case_id": packet["case_id"],
        "authoritative_conversation": packet["authoritative_conversation"],
        "authoritative_conversation_sha256": packet[
            "authoritative_conversation_sha256"
        ],
        "source_turn_numbers": list(packet["source_turn_numbers"]),
        "preservation_material": copy.deepcopy(packet["preservation_material"]),
        "disposition_ledger": copy.deepcopy(ledger),
        "instructions": {
            "dispositions_are_frozen": True,
            "candidate_deletion_allowed": False,
            "include_only_earned_public_friction": True,
            "private_guardrails_must_not_leak": True,
            "preserve_useful_original_reasoning": True,
            "unsupported_case_facts_allowed": False,
        },
    }
    value["synthesis_packet_sha256"] = value_sha256(value)
    return value


def synthesis_prompts(synthesis_packet: Mapping[str, Any]) -> dict[str, str]:
    system = (
        "You are a fresh-context answer synthesizer. The supplied disposition ledger "
        "is already frozen. Draft a self-contained answer using only source-grounded, "
        "earned public friction. Do not change dispositions, expose private guardrails, "
        "invent facts, or display mental-model machinery. Return only requested JSON."
    )
    user = (
        "R3 FROZEN DISPOSITION SYNTHESIS PACKET\n"
        + canonical(synthesis_packet)
        + "\n\nPreserve useful original advice. An unchanged conclusion and public stand-down "
        "are valid. Summarize only factual changes and classify preservation honestly."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": text_sha256(system),
        "user_prompt_sha256": text_sha256(user),
    }


def synthesis_stage_request_body(
    *, base_body: Mapping[str, Any], synthesis_packet: Mapping[str, Any]
) -> dict[str, Any]:
    return _request_body(
        base_body=base_body,
        prompts=synthesis_prompts(synthesis_packet),
        schema=synthesis_response_schema(),
        name="lolla_r3_separated_answer_synthesis",
        maximum_output_tokens=SYNTHESIS_STAGE_MAX_OUTPUT_TOKENS,
    )


def compile_separated_synthesis_response(
    *, response: Mapping[str, Any], packet: Mapping[str, Any], ledger: Mapping[str, Any]
) -> dict[str, Any]:
    validate_disposition_ledger(ledger, packet=packet)
    if set(response) != set(SYNTHESIS_FIELDS):
        raise R3TaskShapeError("synthesis response envelope is invalid")
    canonical_response = {
        "candidate_dispositions": copy.deepcopy(ledger["candidate_dispositions"]),
        "reconsidered_answer": _bounded_text(
            response.get("reconsidered_answer"),
            field="reconsidered_answer",
            maximum=RECONSIDERED_ANSWER_MAX,
            allow_empty=False,
        ),
        "change_summary": _bounded_text(
            response.get("change_summary"),
            field="change_summary",
            maximum=CHANGE_SUMMARY_MAX,
            allow_empty=False,
        ),
        "original_answer_preservation": response.get("original_answer_preservation"),
    }
    result = compile_pressure_response(response=canonical_response, packet=packet)
    result["separated_synthesis"] = {
        "schema_version": COUNTERFACTUAL_SCHEMA,
        "disposition_ledger_sha256": ledger["ledger_sha256"],
        "dispositions_changed_by_synthesis": False,
        "semantic_applicability_inferred_by_code": False,
    }
    return result


def request_metrics(body: Mapping[str, Any]) -> dict[str, Any]:
    prompt_tokens = estimated_tokens({
        key: value for key, value in body.items() if key != "max_tokens"
    })
    output_tokens = int(body.get("max_tokens", 0) or 0)
    maximum_cost = round(
        prompt_tokens * MAX_PROMPT_PRICE / 1_000_000
        + output_tokens * MAX_COMPLETION_PRICE / 1_000_000,
        9,
    )
    schema = body["response_format"]["json_schema"]["schema"]
    messages = body.get("messages", [])
    return {
        "request_body_sha256": value_sha256(body),
        "estimated_prompt_tokens": prompt_tokens,
        "maximum_output_tokens": output_tokens,
        "maximum_estimated_cost_usd": maximum_cost,
        "system_prompt_sha256": text_sha256(messages[0]["content"]),
        "user_prompt_sha256": text_sha256(messages[1]["content"]),
        "user_prompt_utf8_bytes": len(messages[1]["content"].encode("utf-8")),
        "response_schema_sha256": value_sha256(schema),
        "response_schema_metrics": schema_metrics(schema),
    }


def frozen_responsibility_map() -> list[dict[str, Any]]:
    """Declare responsibilities; counts are descriptive, never a quality score."""

    def row(
        identity: str,
        owner: str,
        responsibility: str,
        stages: tuple[bool, bool, bool, bool],
    ) -> dict[str, Any]:
        current, collapsed, disposition_stage, synthesis_stage = stages
        return {
            "id": identity,
            "owner": owner,
            "responsibility": responsibility,
            "current": current,
            "collapsed": collapsed,
            "disposition_stage": disposition_stage,
            "synthesis_stage": synthesis_stage,
        }

    return [
        row("s1", "llm", "attempt strongest application", (True, True, True, False)),
        row("s2", "llm", "identify exact supporting turns", (True, True, True, False)),
        row("s3", "llm", "choose apply reject or park", (True, True, True, False)),
        row("s4", "llm", "choose material effect category", (True, True, True, False)),
        row(
            "s5",
            "llm",
            "choose public or private effect custody",
            (True, True, True, False),
        ),
        row("s6", "llm", "explain source-grounded judgment", (True, True, True, False)),
        row(
            "s7",
            "llm",
            "state failed reopen or falsifier boundary",
            (True, True, True, False),
        ),
        row("s8", "llm", "draft reconsidered answer", (True, True, False, True)),
        row("s9", "llm", "summarize change or stand-down", (True, True, False, True)),
        row(
            "s10",
            "llm",
            "classify original-answer preservation",
            (True, True, False, True),
        ),
        row(
            "d1",
            "deterministic",
            "validate pressure identity and packet order",
            (True, True, True, True),
        ),
        row(
            "d2",
            "deterministic",
            "validate source turn custody and text bounds",
            (True, True, True, True),
        ),
        row(
            "d3",
            "deterministic",
            "map explicit controlled outcome label",
            (False, True, True, False),
        ),
        row(
            "d4",
            "deterministic",
            "validate explicit effect custody combinations",
            (True, True, True, True),
        ),
        row(
            "d5",
            "deterministic",
            "restore immutable model and risk fields",
            (True, True, True, True),
        ),
        row(
            "d6",
            "deterministic",
            "hash artifacts budget calls and terminal status",
            (True, True, True, True),
        ),
    ]


def describe_cross_field_surfaces() -> list[dict[str, Any]]:
    return [
        {
            "surface": "disposition_effect",
            "current": "independent labels can contradict",
            "collapsed": "one controlled outcome label; exact contradiction impossible",
            "semantic_judgment_owner": "llm",
        },
        {
            "surface": "disposition_effect_custody",
            "current": "apply requires public/private text; reject/park require empty text",
            "collapsed": "unchanged and still fail-closed",
            "semantic_judgment_owner": "llm",
        },
        {
            "surface": "disposition_boundary_role",
            "current": "one boundary field mapped by disposition",
            "collapsed": "one boundary field mapped by explicit outcome",
            "semantic_judgment_owner": "llm",
        },
        {
            "surface": "dispositions_answer",
            "current": "same generation judges pressure and drafts answer",
            "collapsed": "same as current",
            "separated": "frozen ledger transferred to a distinct synthesis task",
            "semantic_judgment_owner": "llm",
        },
    ]


def canonical_json_bytes(value: Any) -> int:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return len(encoded)
