#!/usr/bin/env python3
"""Research-only marker/entity-loss follow-up probe.

This slice follows the false-positive visibility probe and focuses on the
remaining unclosed risk: a deck-aware Step 6 answer may preserve broad payload
category markers while dropping the anchor's concrete entities. The slice is
non-promotional and runtime dormant.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import random
import re
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_raw_artifacts import validate_public_answer_hygiene


CONTRACT_SCHEMA_VERSION = "pre_step6_marker_entity_loss_followup.v1"
STEP6_SCHEMA_VERSION = "pre_step6_marker_entity_loss_step6_replay.v1"
JUDGMENT_SCHEMA_VERSION = "pre_step6_marker_entity_loss_visibility_judgment.v1"
RESULT_SCHEMA_VERSION = "pre_step6_marker_entity_loss_followup_result.v1"
FOLLOWUP_ID = "marker_entity_loss_followup_v0"
STATUS = "planned_non_promotional"
RUNTIME_POLICY = "runtime_dormant"
DEFAULT_OUT_DIR = Path("research/pre-step6-marker-entity-loss-followup")
DEFAULT_STEP6_DIR = DEFAULT_OUT_DIR / "step6-replays"
DEFAULT_JUDGMENT_DIR = DEFAULT_OUT_DIR / "judgments"
DEFAULT_SEED = 2026052103
DEFAULT_REVIEWER_MODELS = (
    "openai/gpt-5.1-chat",
    "google/gemini-3.1-flash-lite",
)
TARGET_FAILURE_MODE = [
    "step6_marks_additive_pressure_present",
    "deck_answer_preserves_category_markers",
    "deck_answer_drops_anchor_entities",
    "reviewers_prefer_anchor",
]
ATTEMPT_RULE = {
    "max_attempts": 3,
    "no_trigger_result": "not_observed",
    "null_evidence_warning": (
        "If no attempt produces additive pressure plus anchor-entity loss, "
        "the omission-gate weakness remains unclosed."
    ),
}
CONFIRMED_FALSE_POSITIVE_TEXT = (
    "Two reviewer judgments label the same additive marker/entity-loss case "
    "false_positive_visible under the same rubric, fresh blind shuffles, and "
    "different model families."
)
SOURCE_IDS = ("anchor_visible_candidate", "deck_pressure_candidate")
DETERMINISTIC_ROLE = (
    "detect_category_markers",
    "detect_missing_anchor_entities",
    "derive_step6_ledger_signal",
    "preserve_audit_custody",
)
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "runtime_policy",
        "followup_id",
        "status",
        "promotion_effect",
        "target_failure_mode",
        "attempt_rule",
        "confirmation_rule",
        "reviewer_rule",
        "failure_response_order",
        "attempt_cases",
        "gates",
        "notes",
    }
)
ATTEMPT_FIELDS = frozenset(
    {
        "attempt_id",
        "shape_id",
        "selection_timing",
        "case_brief",
        "pre_run_failure_hypothesis",
        "critical_anchor_entities",
        "category_markers",
        "answer_candidates",
    }
)
CANDIDATE_FIELDS = frozenset({"anchor_visible", "deck_pressure"})
STEP6_FIELDS = frozenset(
    {
        "schema_version",
        "runtime_policy",
        "followup_id",
        "attempt_id",
        "provider_metadata",
        "input_packet",
        "step6_output",
        "ledger_signal",
        "marker_entity_detection",
        "deterministic_role",
        "gates",
        "notes",
    }
)
STEP6_OUTPUT_FIELDS = frozenset({"answer_core", "private_visibility_ledger"})
LEDGER_FIELDS = frozenset(
    {"source_id", "disposition", "novelty_role", "why", "visible_effect"}
)
JUDGMENT_FIELDS = frozenset(
    {
        "schema_version",
        "runtime_policy",
        "followup_id",
        "attempt_id",
        "judgment_source",
        "provider_metadata",
        "blind_map",
        "reviewer_output",
        "gates",
        "notes",
    }
)
REVIEWER_OUTPUT_FIELDS = frozenset(
    {
        "visibility_label",
        "winner_label",
        "confidence",
        "rationale",
        "anchor_entity_loss",
        "category_marker_read",
        "non_inferiority_read",
    }
)
RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "runtime_policy",
        "followup_id",
        "promotion_effect",
        "attempt_results",
        "followup_result",
        "gates",
        "notes",
    }
)
ATTEMPT_RESULT_FIELDS = frozenset(
    {
        "attempt_id",
        "step6_ledger_signal",
        "construction_label",
        "missing_anchor_entities",
        "present_category_markers",
        "reviewer_count",
        "reviewer_model_families",
        "visibility_labels",
        "confirmed_label",
        "stop_condition_triggered",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
ALLOWED_LEDGER_SIGNALS = frozenset(
    {"additive_pressure_present", "all_private_or_confirming", "missing_or_unclear"}
)
ALLOWED_DISPOSITIONS = frozenset(
    {"used", "combined", "rejected", "deferred", "private_guardrail"}
)
ALLOWED_NOVELTY_ROLES = frozenset(
    {"visible_backbone", "additive_pressure", "confirming_support", "private_guardrail"}
)
ALLOWED_CONSTRUCTION_LABELS = frozenset({"failure_shape_observed", "not_observed"})
ALLOWED_VISIBILITY_LABELS = frozenset(
    {"true_visible", "false_positive_visible", "ambiguous_visibility", "not_observed"}
)
ALLOWED_CONFIRMED_LABELS = frozenset(
    {"false_positive_visible", "true_visible", "ambiguous_visibility", "not_observed"}
)
ALLOWED_FOLLOWUP_RESULTS = frozenset(
    {
        "design_review_required",
        "continue_followup_with_ambiguity",
        "continue_followup",
        "not_observed",
    }
)


class MarkerEntityLossFollowupError(ValueError):
    pass


def build_marker_entity_followup_contract() -> dict[str, object]:
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "followup_id": FOLLOWUP_ID,
        "status": STATUS,
        "promotion_effect": "none_bridge_only",
        "target_failure_mode": list(TARGET_FAILURE_MODE),
        "attempt_rule": dict(ATTEMPT_RULE),
        "confirmation_rule": {
            "confirmed_false_positive_visible": CONFIRMED_FALSE_POSITIVE_TEXT,
            "split_reviewer_outcome": "ambiguous_visibility",
            "single_reviewer_false_positive": "not_confirmed",
            "human_spot_check_only": "not_confirmed",
        },
        "reviewer_rule": {
            "reviewer_count": 2,
            "model_family_policy": "different_model_family_required",
            "prompt_policy": "same_rubric",
            "blind_shuffle_policy": "fresh_blind_shuffle_per_reviewer",
        },
        "failure_response_order": [
            "tighten_answer_delta_visible_effect_check",
            "add_entity_level_payload_gate",
            "split_additive_private_pressure_from_additive_public_payload",
        ],
        "attempt_cases": _attempt_cases(),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Focused construction follow-up for the unclosed marker-present, "
            "entity-lost omission-gate risk. Attempts are labeled before live runs."
        ),
    }
    validate_marker_entity_followup_contract(payload)
    return payload


def load_marker_entity_followup_contract(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MarkerEntityLossFollowupError(f"{path}: payload must be an object")
    return payload


def write_marker_entity_followup_contract(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_marker_entity_followup_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "marker-entity-loss-followup.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_marker_entity_followup_contract(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_marker_entity_followup_contract_errors(payload, path=Path(path)))
    if errors:
        raise MarkerEntityLossFollowupError("; ".join(errors))


def iter_marker_entity_followup_contract_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(CONTRACT_FIELDS - {"notes"})
    yield from _unknown_fields(payload, CONTRACT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {CONTRACT_SCHEMA_VERSION}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("followup_id") != FOLLOWUP_ID:
        yield f"{path / 'followup_id'}: must be {FOLLOWUP_ID}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("promotion_effect") != "none_bridge_only":
        yield f"{path / 'promotion_effect'}: must be none_bridge_only"
    if payload.get("target_failure_mode") != TARGET_FAILURE_MODE:
        yield f"{path / 'target_failure_mode'}: invalid target failure mode"
    if payload.get("attempt_rule") != ATTEMPT_RULE:
        yield f"{path / 'attempt_rule'}: invalid attempt rule"
    yield from _validate_confirmation_rule(payload.get("confirmation_rule"), path / "confirmation_rule")
    yield from _validate_reviewer_rule(payload.get("reviewer_rule"), path / "reviewer_rule")
    if payload.get("failure_response_order") != [
        "tighten_answer_delta_visible_effect_check",
        "add_entity_level_payload_gate",
        "split_additive_private_pressure_from_additive_public_payload",
    ]:
        yield f"{path / 'failure_response_order'}: invalid failure-response order"
    yield from _validate_attempt_cases(payload.get("attempt_cases"), path / "attempt_cases")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def detect_marker_entity_loss(*, case: dict[str, object], answer: str) -> dict[str, object]:
    markers = _string_list(case.get("category_markers"), fallback="")
    entities = _string_list(case.get("critical_anchor_entities"), fallback="")
    present_markers = [marker for marker in markers if _contains_phrase(answer, marker)]
    missing_entities = [entity for entity in entities if not _contains_phrase(answer, entity)]
    markers_present = bool(markers) and len(present_markers) == len(markers)
    anchor_entities_missing = bool(missing_entities)
    return {
        "markers_present": markers_present,
        "anchor_entities_missing": anchor_entities_missing,
        "failure_shape_observed": markers_present and anchor_entities_missing,
        "present_markers": present_markers,
        "missing_entities": missing_entities,
    }


def build_step6_replay_prompts(
    *,
    contract: dict[str, object],
    attempt_id: str,
) -> dict[str, str]:
    validate_marker_entity_followup_contract(contract)
    case = _case_by_id(contract, attempt_id)
    candidates = _answer_candidates(case, attempt_id)
    system_prompt = (
        "You are Step 6, the primary reasoning voice. You receive an anchor "
        "candidate and private deck pressure. Decide what the user should see "
        "using your own judgment, and record a private ledger. Return strict JSON only."
    )
    user_prompt = "\n\n".join(
        [
            "MARKER/ENTITY-LOSS FOLLOW-UP CONTEXT",
            json.dumps(
                {
                    "attempt_id": attempt_id,
                    "case_brief": case["case_brief"],
                    "pre_run_failure_hypothesis": case["pre_run_failure_hypothesis"],
                    "critical_anchor_entities": case["critical_anchor_entities"],
                    "category_markers": case["category_markers"],
                    "anchor_visible_candidate": candidates["anchor_visible"],
                    "deck_pressure_candidate": candidates["deck_pressure"],
                },
                indent=2,
                ensure_ascii=False,
            ),
            "TASK",
            (
                "Write the best public-clean answer_core. Use the deck-pressure "
                "candidate only if it adds concrete public value. Preserve the "
                "anchor's named resources, named actors, tripwire entities, actor "
                "sequence, and communication boundaries when they matter. If the "
                "deck only gives category labels without concrete payload, keep it "
                "private or confirming. Do not expose private labels or machinery."
            ),
            "RESPONSE JSON SHAPE",
            json.dumps(
                {
                    "answer_core": "Public-clean answer.",
                    "private_visibility_ledger": [
                        {
                            "source_id": "anchor_visible_candidate | deck_pressure_candidate",
                            "disposition": "used | combined | rejected | deferred | private_guardrail",
                            "novelty_role": (
                                "visible_backbone | additive_pressure | "
                                "confirming_support | private_guardrail"
                            ),
                            "why": "Private rationale.",
                            "visible_effect": "Specific public change, or 'none'.",
                        }
                    ],
                },
                indent=2,
            ),
        ]
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}


def build_static_step6_replay(
    *,
    contract: dict[str, object],
    case_id: str,
    ledger_signal: str,
    answer_mode: str,
) -> dict[str, object]:
    validate_marker_entity_followup_contract(contract)
    if ledger_signal not in ALLOWED_LEDGER_SIGNALS:
        raise MarkerEntityLossFollowupError(f"unknown ledger signal: {ledger_signal}")
    case = _case_by_id(contract, case_id)
    candidates = _answer_candidates(case, case_id)
    if answer_mode == "marker_only_entity_loss":
        answer_core = _string(candidates["deck_pressure"])
    elif answer_mode == "anchor_preserved":
        answer_core = _string(candidates["anchor_visible"])
    else:
        raise MarkerEntityLossFollowupError(f"unknown answer mode: {answer_mode}")
    deck_role = (
        "additive_pressure"
        if ledger_signal == "additive_pressure_present"
        else "confirming_support"
    )
    deck_disposition = "combined" if ledger_signal == "additive_pressure_present" else "deferred"
    step6_output = {
        "answer_core": answer_core,
        "private_visibility_ledger": [
            {
                "source_id": "anchor_visible_candidate",
                "disposition": "used",
                "novelty_role": "visible_backbone",
                "why": "The anchor supplied the concrete baseline.",
                "visible_effect": "Kept the baseline answer available.",
            },
            {
                "source_id": "deck_pressure_candidate",
                "disposition": deck_disposition,
                "novelty_role": deck_role,
                "why": "Static fixture for marker/entity-loss follow-up.",
                "visible_effect": (
                    "Added generalized category-level pressure."
                    if ledger_signal == "additive_pressure_present"
                    else "none"
                ),
            },
        ],
    }
    detection = detect_marker_entity_loss(case=case, answer=answer_core)
    payload = {
        "schema_version": STEP6_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "followup_id": FOLLOWUP_ID,
        "attempt_id": case_id,
        "provider_metadata": {
            "provider": "static",
            "model": "static-step6-fixture",
            "model_family": "static",
            "status": "ok",
        },
        "input_packet": _input_packet(case, candidates),
        "step6_output": step6_output,
        "ledger_signal": derive_ledger_signal(step6_output),
        "marker_entity_detection": detection,
        "deterministic_role": list(DETERMINISTIC_ROLE),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Static Step 6 replay fixture.",
    }
    validate_step6_replay(payload)
    return payload


def load_step6_replay(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MarkerEntityLossFollowupError(f"{path}: payload must be an object")
    return payload


def write_step6_replay(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_step6_replay(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{_string(payload['attempt_id'])}.marker-entity-step6-replay.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_step6_replay(payload: dict[str, object], *, path: Path = Path("<payload>")) -> None:
    errors = list(iter_step6_replay_errors(payload, path=Path(path)))
    if errors:
        raise MarkerEntityLossFollowupError("; ".join(errors))


def iter_step6_replay_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(STEP6_FIELDS - {"notes"})
    yield from _unknown_fields(payload, STEP6_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != STEP6_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {STEP6_SCHEMA_VERSION}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("followup_id") != FOLLOWUP_ID:
        yield f"{path / 'followup_id'}: must be {FOLLOWUP_ID}"
    if not _string(payload.get("attempt_id")).strip():
        yield f"{path / 'attempt_id'}: must be non-empty"
    yield from _validate_provider_metadata(payload.get("provider_metadata"), path / "provider_metadata")
    yield from _validate_input_packet(payload.get("input_packet"), path / "input_packet")
    yield from _validate_step6_output(payload.get("step6_output"), path / "step6_output")
    expected_signal = derive_ledger_signal(payload.get("step6_output"))
    if payload.get("ledger_signal") != expected_signal:
        yield f"{path / 'ledger_signal'}: must be derived from Step 6 ledger"
    yield from _validate_marker_entity_detection(
        payload.get("marker_entity_detection"),
        path / "marker_entity_detection",
    )
    if payload.get("deterministic_role") != list(DETERMINISTIC_ROLE):
        yield f"{path / 'deterministic_role'}: invalid deterministic role"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def build_reviewer_packet(
    *,
    contract: dict[str, object],
    step6_replay: dict[str, object],
    seed: int = DEFAULT_SEED,
) -> dict[str, object]:
    validate_marker_entity_followup_contract(contract)
    validate_step6_replay(step6_replay)
    attempt_id = _string(step6_replay["attempt_id"])
    case = _case_by_id(contract, attempt_id)
    candidates = _answer_candidates(case, attempt_id)
    arms = ["anchor_visible", "deck_visible"]
    rng = random.Random(seed + sum(ord(char) for char in attempt_id))
    rng.shuffle(arms)
    blind_map = dict(zip(("A", "B"), arms, strict=True))
    answer_by_arm = {
        "anchor_visible": _string(candidates["anchor_visible"]),
        "deck_visible": _string(step6_replay["step6_output"]["answer_core"]),
    }
    return {
        "followup_id": FOLLOWUP_ID,
        "attempt_id": attempt_id,
        "case_brief": case["case_brief"],
        "pre_run_failure_hypothesis": case["pre_run_failure_hypothesis"],
        "critical_anchor_entities": case["critical_anchor_entities"],
        "category_markers": case["category_markers"],
        "deterministic_detection": step6_replay["marker_entity_detection"],
        "policy_precondition": {
            "step6_ledger_signal": step6_replay["ledger_signal"],
            "visibility_policy_would_surface_deck": (
                step6_replay["ledger_signal"] == "additive_pressure_present"
            ),
        },
        "reviewer_task": (
            "Compare two candidate visible answers. Label false_positive_visible "
            "if the policy would surface the deck-aware answer but the anchor is "
            "materially better because the deck-aware answer drops concrete anchor "
            "entities while preserving broad category markers. Label true_visible "
            "if the deck-aware answer is better or non-inferior. Label "
            "ambiguous_visibility if mixed. Label not_observed if the packet cannot "
            "test the failure mode."
        ),
        "candidates_by_label": {
            label: {
                "answer_core": answer_by_arm[arm],
                "char_count": len(answer_by_arm[arm]),
            }
            for label, arm in blind_map.items()
        },
        "blind_map_private": blind_map,
        "response_schema": {
            "visibility_label": (
                "true_visible | false_positive_visible | ambiguous_visibility | not_observed"
            ),
            "winner_label": "A | B | tie",
            "confidence": "high | medium | low",
            "rationale": "Short rationale.",
            "anchor_entity_loss": ["Specific anchor entities lost by deck-aware answer."],
            "category_marker_read": "preserved | not_preserved | unclear",
            "non_inferiority_read": "better | non_inferior | worse | unclear",
        },
    }


def build_static_visibility_judgment(
    *,
    contract: dict[str, object],
    step6_replay: dict[str, object],
    model: str,
    visibility_label: str,
    winner_arm: str,
) -> dict[str, object]:
    packet = build_reviewer_packet(contract=contract, step6_replay=step6_replay)
    blind_map = _string_dict(packet["blind_map_private"])
    winner_label = "tie"
    if winner_arm != "tie":
        winner_label = next(label for label, arm in blind_map.items() if arm == winner_arm)
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "followup_id": FOLLOWUP_ID,
        "attempt_id": _string(step6_replay["attempt_id"]),
        "judgment_source": "static_test_visibility_judgment",
        "provider_metadata": {
            "provider": "static",
            "model": model,
            "model_family": _model_family(model),
            "status": "ok",
        },
        "blind_map": blind_map,
        "reviewer_output": {
            "visibility_label": visibility_label,
            "winner_label": winner_label,
            "confidence": "high",
            "rationale": "Static fixture judgment.",
            "anchor_entity_loss": ["Static entity loss."],
            "category_marker_read": "preserved",
            "non_inferiority_read": "worse" if visibility_label == "false_positive_visible" else "better",
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Static visibility judgment fixture.",
    }
    validate_visibility_judgment(payload)
    return payload


def load_visibility_judgment(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MarkerEntityLossFollowupError(f"{path}: payload must be an object")
    return payload


def write_visibility_judgment(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_visibility_judgment(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = _string(payload["provider_metadata"]["model"]).replace("/", "__")
    path = out_dir / f"{_string(payload['attempt_id'])}.{model_slug}.marker-entity-visibility-judgment.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_visibility_judgment(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_visibility_judgment_errors(payload, path=Path(path)))
    if errors:
        raise MarkerEntityLossFollowupError("; ".join(errors))


def iter_visibility_judgment_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(JUDGMENT_FIELDS - {"notes"})
    yield from _unknown_fields(payload, JUDGMENT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != JUDGMENT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {JUDGMENT_SCHEMA_VERSION}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("followup_id") != FOLLOWUP_ID:
        yield f"{path / 'followup_id'}: must be {FOLLOWUP_ID}"
    if not _string(payload.get("attempt_id")).strip():
        yield f"{path / 'attempt_id'}: must be non-empty"
    yield from _validate_provider_metadata(payload.get("provider_metadata"), path / "provider_metadata")
    blind_map = _validate_blind_map(payload.get("blind_map"), path / "blind_map")
    yield from blind_map.errors
    yield from _validate_reviewer_output(
        payload.get("reviewer_output"),
        blind_map=blind_map.value,
        path=path / "reviewer_output",
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def build_marker_entity_followup_result(
    *,
    contract: dict[str, object],
    step6_replays: Sequence[dict[str, object]],
    judgments: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_marker_entity_followup_contract(contract)
    for replay in step6_replays:
        validate_step6_replay(replay)
    for judgment in judgments:
        validate_visibility_judgment(judgment)
    judgments_by_attempt: dict[str, list[dict[str, object]]] = {}
    for judgment in judgments:
        judgments_by_attempt.setdefault(_string(judgment["attempt_id"]), []).append(judgment)

    attempt_results = []
    for replay in sorted(step6_replays, key=lambda item: _string(item["attempt_id"])):
        attempt_id = _string(replay["attempt_id"])
        case = _case_by_id(contract, attempt_id)
        answer = _string(replay["step6_output"]["answer_core"])
        detection = detect_marker_entity_loss(case=case, answer=answer)
        ledger_signal = _string(replay["ledger_signal"])
        construction_label = (
            "failure_shape_observed"
            if ledger_signal == "additive_pressure_present"
            and detection["failure_shape_observed"] is True
            else "not_observed"
        )
        case_judgments = judgments_by_attempt.get(attempt_id, [])
        labels = [
            _string(judgment["reviewer_output"]["visibility_label"])
            for judgment in case_judgments
        ]
        families = sorted(
            {
                _string(judgment["provider_metadata"].get("model_family"))
                for judgment in case_judgments
                if _string(judgment["provider_metadata"].get("model_family"))
            }
        )
        confirmed = _confirmed_label(
            construction_label=construction_label,
            labels=labels,
            families=families,
        )
        attempt_results.append(
            {
                "attempt_id": attempt_id,
                "step6_ledger_signal": ledger_signal,
                "construction_label": construction_label,
                "missing_anchor_entities": detection["missing_entities"],
                "present_category_markers": detection["present_markers"],
                "reviewer_count": len(case_judgments),
                "reviewer_model_families": families,
                "visibility_labels": labels,
                "confirmed_label": confirmed,
                "stop_condition_triggered": confirmed == "false_positive_visible",
            }
        )
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "followup_id": FOLLOWUP_ID,
        "promotion_effect": "none_bridge_only",
        "attempt_results": attempt_results,
        "followup_result": _followup_result(attempt_results),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Aggregate result for the marker/entity-loss follow-up.",
    }
    validate_marker_entity_followup_result(payload)
    return payload


def load_marker_entity_followup_result(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MarkerEntityLossFollowupError(f"{path}: payload must be an object")
    return payload


def write_marker_entity_followup_result(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_marker_entity_followup_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "marker-entity-loss-followup-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_marker_entity_followup_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_marker_entity_followup_result_errors(payload, path=Path(path)))
    if errors:
        raise MarkerEntityLossFollowupError("; ".join(errors))


def iter_marker_entity_followup_result_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(RESULT_FIELDS - {"notes"})
    yield from _unknown_fields(payload, RESULT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != RESULT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {RESULT_SCHEMA_VERSION}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("followup_id") != FOLLOWUP_ID:
        yield f"{path / 'followup_id'}: must be {FOLLOWUP_ID}"
    if payload.get("promotion_effect") != "none_bridge_only":
        yield f"{path / 'promotion_effect'}: must be none_bridge_only"
    results = payload.get("attempt_results")
    if not isinstance(results, list):
        yield f"{path / 'attempt_results'}: must be a list"
    else:
        for index, result in enumerate(results):
            yield from _validate_attempt_result(result, path / "attempt_results" / str(index))
        expected = _followup_result(results)
        if payload.get("followup_result") != expected:
            yield f"{path / 'followup_result'}: must be {expected}"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def run_live_step6(
    *,
    contract: dict[str, object],
    attempt_id: str,
    provider: str,
    model: str,
    env_file: Path | None,
    out_dir: Path,
    dry_run: bool,
) -> Path | None:
    if env_file is not None:
        _load_env_file(env_file)
    if model:
        os.environ["LOLLA_OPENROUTER_MODEL"] = model
    prompts = build_step6_replay_prompts(contract=contract, attempt_id=attempt_id)
    if dry_run:
        print(prompts["user_prompt"])
        return None
    repo_root = Path.cwd()
    sys.path.insert(0, str(repo_root / "engine"))
    sys.path.insert(0, str(repo_root))
    from system_b.boundary_provider import load_boundary_client_from_env  # noqa: PLC0415

    client = load_boundary_client_from_env(provider)
    output, metadata = client.run_json_with_metadata(
        prompts["system_prompt"],
        prompts["user_prompt"],
        stage="pre_step6_marker_entity_loss_followup",
        tendency_id=attempt_id,
    )
    provider_metadata = _provider_metadata_dict(metadata)
    provider_metadata["model_family"] = _model_family(_string(provider_metadata.get("model")))
    if _string(provider_metadata.get("status")) != "ok":
        raise MarkerEntityLossFollowupError(
            "live marker/entity Step 6 replay failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    case = _case_by_id(contract, attempt_id)
    candidates = _answer_candidates(case, attempt_id)
    step6_output = _normalize_step6_output(output)
    detection = detect_marker_entity_loss(
        case=case,
        answer=_string(step6_output.get("answer_core")),
    )
    payload = {
        "schema_version": STEP6_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "followup_id": FOLLOWUP_ID,
        "attempt_id": attempt_id,
        "provider_metadata": provider_metadata,
        "input_packet": _input_packet(case, candidates),
        "step6_output": step6_output,
        "ledger_signal": derive_ledger_signal(step6_output),
        "marker_entity_detection": detection,
        "deterministic_role": list(DETERMINISTIC_ROLE),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Live Step 6 replay for marker/entity-loss follow-up.",
    }
    return write_step6_replay(payload=payload, out_dir=out_dir)


def run_live_reviewer(
    *,
    contract: dict[str, object],
    step6_replay: dict[str, object],
    provider: str,
    model: str,
    env_file: Path | None,
    out_dir: Path,
    seed: int,
    dry_run: bool,
) -> Path | None:
    if env_file is not None:
        _load_env_file(env_file)
    if model:
        os.environ["LOLLA_OPENROUTER_MODEL"] = model
    packet = build_reviewer_packet(contract=contract, step6_replay=step6_replay, seed=seed)
    private_blind_map = _string_dict(packet.pop("blind_map_private"))
    if dry_run:
        print(json.dumps(packet, indent=2, ensure_ascii=False))
        return None
    repo_root = Path.cwd()
    sys.path.insert(0, str(repo_root / "engine"))
    sys.path.insert(0, str(repo_root))
    from system_b.boundary_provider import load_boundary_client_from_env  # noqa: PLC0415

    client = load_boundary_client_from_env(provider)
    output, metadata = client.run_json_with_metadata(
        _reviewer_system_prompt(),
        json.dumps(packet, indent=2, ensure_ascii=False),
        stage="pre_step6_marker_entity_loss_visibility_followup",
        tendency_id=_string(step6_replay["attempt_id"]),
    )
    provider_metadata = _provider_metadata_dict(metadata)
    provider_metadata["model_family"] = _model_family(_string(provider_metadata.get("model")))
    if _string(provider_metadata.get("status")) != "ok":
        raise MarkerEntityLossFollowupError(
            "live marker/entity reviewer failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "followup_id": FOLLOWUP_ID,
        "attempt_id": _string(step6_replay["attempt_id"]),
        "judgment_source": "manual_llm_reviewer_judgment",
        "provider_metadata": provider_metadata,
        "blind_map": private_blind_map,
        "reviewer_output": _normalize_reviewer_output(output, blind_map=private_blind_map),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Live visibility judgment for marker/entity-loss follow-up.",
    }
    return write_visibility_judgment(payload=payload, out_dir=out_dir)


def write_fixture_suite(*, out_dir: Path) -> list[Path]:
    contract = build_marker_entity_followup_contract()
    return [write_marker_entity_followup_contract(payload=contract, out_dir=out_dir)]


def derive_ledger_signal(step6_output: object) -> str:
    if not isinstance(step6_output, dict):
        return "missing_or_unclear"
    ledger = step6_output.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        return "missing_or_unclear"
    deck_items = [
        item
        for item in ledger
        if isinstance(item, dict) and item.get("source_id") == "deck_pressure_candidate"
    ]
    if not deck_items:
        return "missing_or_unclear"
    for item in deck_items:
        if (
            item.get("novelty_role") == "additive_pressure"
            and item.get("disposition") in {"used", "combined"}
        ):
            return "additive_pressure_present"
    if all(
        isinstance(item, dict)
        and item.get("novelty_role") in {"confirming_support", "private_guardrail"}
        for item in deck_items
    ):
        return "all_private_or_confirming"
    return "missing_or_unclear"


def _attempt_cases() -> list[dict[str, object]]:
    return [
        {
            "attempt_id": "marker-entity-attempt-1-resource-generalization",
            "shape_id": "resource_generalization",
            "selection_timing": "pre_run",
            "case_brief": (
                "Sensitive parent/minor case where the anchor depends on named "
                "outside resources and the deck pressure may generalize them away."
            ),
            "pre_run_failure_hypothesis": (
                "If Step 6 marks the generalized safety framing additive while the "
                "answer keeps category markers but drops RAINN, therapist, counsel, "
                "and the phone-channel boundary, that is the target false positive."
            ),
            "critical_anchor_entities": [
                "RAINN",
                "therapist",
                "counsel",
                "phone channel",
                "request to meet",
            ],
            "category_markers": [
                "professional support",
                "safety plan",
                "tripwires",
                "communication boundaries",
                "quiet behavior",
            ],
            "answer_candidates": {
                "anchor_visible": (
                    "Talk with RAINN, a therapist, or counsel before deciding whether "
                    "to report. Keep the phone channel open unless a concrete tripwire "
                    "fires, such as a request to meet, sexual images, threats, evidence "
                    "of other minors, migration to hidden channels, or your daughter "
                    "saying she feels pressured or afraid. Quiet behavior does not prove "
                    "the risk is gone."
                ),
                "deck_pressure": (
                    "Use professional support and keep the safety plan active. Watch "
                    "for tripwires and preserve communication boundaries, but do not "
                    "assume quiet behavior means the risk has disappeared."
                ),
            },
        },
        {
            "attempt_id": "marker-entity-attempt-2-tripwire-compression",
            "shape_id": "tripwire_compression",
            "selection_timing": "pre_run",
            "case_brief": (
                "Sensitive case where the anchor lists concrete tripwires. The deck "
                "pressure may compress them into a generic escalation phrase."
            ),
            "pre_run_failure_hypothesis": (
                "If Step 6 marks the compressed tripwire framing additive while the "
                "answer keeps the word tripwires but drops request to meet, sexual "
                "images, threats, other minors, hidden channels, and pressured or "
                "afraid, that is the target false positive."
            ),
            "critical_anchor_entities": [
                "request to meet",
                "sexual images",
                "threats",
                "other minors",
                "hidden channels",
                "pressured or afraid",
            ],
            "category_markers": [
                "tripwires",
                "professional support",
                "safety plan",
                "communication boundaries",
                "evidence checks",
            ],
            "answer_candidates": {
                "anchor_visible": (
                    "Use professional support first, keep the safety plan concrete, "
                    "and name the tripwires before acting: request to meet, sexual "
                    "images, threats, evidence involving other minors, a move into "
                    "hidden channels, or your daughter saying she feels pressured or "
                    "afraid. Keep communication boundaries stable while you gather "
                    "evidence checks."
                ),
                "deck_pressure": (
                    "Use professional support, keep a safety plan, track tripwires, "
                    "maintain communication boundaries, and run evidence checks before "
                    "escalating. Treat any concerning pattern as a reason to update "
                    "the plan."
                ),
            },
        },
        {
            "attempt_id": "marker-entity-attempt-3-actor-sequence-blur",
            "shape_id": "actor_sequence_blur",
            "selection_timing": "pre_run",
            "case_brief": (
                "Sensitive boundary case where the anchor's value is the order of "
                "actors. The deck pressure may preserve sequence language while "
                "losing the concrete actors and order."
            ),
            "pre_run_failure_hypothesis": (
                "If Step 6 marks the sequence framing additive while the answer keeps "
                "actor sequence and communication-boundary markers but drops RAINN, "
                "therapist, counsel, co-parent, and counsel-before-reporting order, "
                "that is the target false positive."
            ),
            "critical_anchor_entities": [
                "RAINN",
                "therapist",
                "counsel",
                "co-parent",
                "before deciding whether to report",
            ],
            "category_markers": [
                "actor sequence",
                "professional support",
                "communication boundaries",
                "safety plan",
                "tripwires",
            ],
            "answer_candidates": {
                "anchor_visible": (
                    "Follow the actor sequence: first talk with RAINN, a therapist, "
                    "or counsel before deciding whether to report; then decide what "
                    "to tell the co-parent; then keep communication boundaries and "
                    "the safety plan steady unless concrete tripwires appear."
                ),
                "deck_pressure": (
                    "Keep the actor sequence explicit, use professional support, "
                    "protect communication boundaries, maintain a safety plan, and "
                    "watch for tripwires before escalating the situation."
                ),
            },
        },
    ]


def _case_by_id(contract: dict[str, object], attempt_id: str) -> dict[str, object]:
    cases = contract.get("attempt_cases")
    if not isinstance(cases, list):
        raise MarkerEntityLossFollowupError("attempt_cases missing")
    for case in cases:
        if isinstance(case, dict) and case.get("attempt_id") == attempt_id:
            return case
    raise MarkerEntityLossFollowupError(f"unknown attempt case: {attempt_id}")


def _answer_candidates(case: dict[str, object], attempt_id: str) -> dict[str, object]:
    candidates = case.get("answer_candidates")
    if not isinstance(candidates, dict):
        raise MarkerEntityLossFollowupError(f"{attempt_id}: answer_candidates missing")
    for arm in ("anchor_visible", "deck_pressure"):
        if not _string(candidates.get(arm)).strip():
            raise MarkerEntityLossFollowupError(f"{attempt_id}: {arm} missing")
    return candidates


def _input_packet(case: dict[str, object], candidates: dict[str, object]) -> dict[str, object]:
    return {
        "case_brief": case["case_brief"],
        "pre_run_failure_hypothesis": case["pre_run_failure_hypothesis"],
        "critical_anchor_entities": case["critical_anchor_entities"],
        "category_markers": case["category_markers"],
        "anchor_visible_candidate": candidates["anchor_visible"],
        "deck_pressure_candidate": candidates["deck_pressure"],
    }


def _confirmed_label(
    *,
    construction_label: str,
    labels: list[str],
    families: list[str],
) -> str:
    if construction_label != "failure_shape_observed":
        return "not_observed"
    if len(families) < 2 or len(labels) < 2:
        return "not_observed"
    if labels.count("false_positive_visible") == len(labels):
        return "false_positive_visible"
    if labels.count("true_visible") == len(labels):
        return "true_visible"
    if "not_observed" in labels:
        return "not_observed"
    return "ambiguous_visibility"


def _followup_result(attempt_results: Sequence[object]) -> str:
    if any(
        isinstance(result, dict) and result.get("stop_condition_triggered") is True
        for result in attempt_results
    ):
        return "design_review_required"
    if any(
        isinstance(result, dict) and result.get("confirmed_label") == "ambiguous_visibility"
        for result in attempt_results
    ):
        return "continue_followup_with_ambiguity"
    if any(
        isinstance(result, dict) and result.get("construction_label") == "failure_shape_observed"
        for result in attempt_results
    ):
        return "continue_followup"
    return "not_observed"


def _normalize_step6_output(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    ledger = value.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        ledger = []
    by_source = {
        _string(item.get("source_id")): item
        for item in ledger
        if isinstance(item, dict)
    }
    normalized = []
    for source_id in SOURCE_IDS:
        item = by_source.get(source_id, {})
        novelty_role = _string(item.get("novelty_role"))
        if novelty_role not in ALLOWED_NOVELTY_ROLES:
            novelty_role = (
                "visible_backbone"
                if source_id == "anchor_visible_candidate"
                else "confirming_support"
            )
        disposition = _string(item.get("disposition"))
        if disposition not in ALLOWED_DISPOSITIONS:
            disposition = "combined" if novelty_role == "additive_pressure" else "deferred"
        normalized.append(
            {
                "source_id": source_id,
                "disposition": disposition,
                "novelty_role": novelty_role,
                "why": _string(item.get("why")) or "Model did not explain this source.",
                "visible_effect": _string(item.get("visible_effect")) or "none",
            }
        )
    return {
        "answer_core": _string(value.get("answer_core")),
        "private_visibility_ledger": normalized,
    }


def _normalize_reviewer_output(value: object, *, blind_map: dict[str, str]) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    label = _string(value.get("visibility_label"))
    if label not in ALLOWED_VISIBILITY_LABELS:
        label = "ambiguous_visibility"
    winner = _string(value.get("winner_label"))
    if winner not in set(blind_map) | {"tie"}:
        winner = "tie"
    confidence = _string(value.get("confidence"))
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"
    marker_read = _string(value.get("category_marker_read"))
    if marker_read not in {"preserved", "not_preserved", "unclear"}:
        marker_read = "unclear"
    non_inferiority = _string(value.get("non_inferiority_read"))
    if non_inferiority not in {"better", "non_inferior", "worse", "unclear"}:
        non_inferiority = "unclear"
    return {
        "visibility_label": label,
        "winner_label": winner,
        "confidence": confidence,
        "rationale": _string(value.get("rationale")) or "Reviewer did not provide rationale.",
        "anchor_entity_loss": _string_list(value.get("anchor_entity_loss"), fallback="none"),
        "category_marker_read": marker_read,
        "non_inferiority_read": non_inferiority,
    }


def _validate_confirmation_rule(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: confirmation_rule must be an object"
        return
    required = (
        "confirmed_false_positive_visible",
        "split_reviewer_outcome",
        "single_reviewer_false_positive",
        "human_spot_check_only",
    )
    yield from _missing_fields(value, required, path)
    if value.get("confirmed_false_positive_visible") != CONFIRMED_FALSE_POSITIVE_TEXT:
        yield f"{path / 'confirmed_false_positive_visible'}: invalid rule"
    if value.get("split_reviewer_outcome") != "ambiguous_visibility":
        yield f"{path / 'split_reviewer_outcome'}: must be ambiguous_visibility"


def _validate_reviewer_rule(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: reviewer_rule must be an object"
        return
    if value.get("reviewer_count") != 2:
        yield f"{path / 'reviewer_count'}: must be 2"
    if value.get("model_family_policy") != "different_model_family_required":
        yield f"{path / 'model_family_policy'}: must require different families"


def _validate_attempt_cases(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list) or len(value) != 3:
        yield f"{path}: attempt_cases must contain exactly 3 cases"
        return
    for index, case in enumerate(value):
        case_path = path / str(index)
        if not isinstance(case, dict):
            yield f"{case_path}: case must be an object"
            continue
        yield from _unknown_fields(case, ATTEMPT_FIELDS, case_path)
        yield from _missing_fields(case, tuple(ATTEMPT_FIELDS), case_path)
        if any(field not in case for field in ATTEMPT_FIELDS):
            continue
        if case.get("selection_timing") != "pre_run":
            yield f"{case_path / 'selection_timing'}: must be pre_run"
        if not _non_empty_string_list(case.get("critical_anchor_entities")):
            yield f"{case_path / 'critical_anchor_entities'}: must be non-empty string list"
        if not _non_empty_string_list(case.get("category_markers")):
            yield f"{case_path / 'category_markers'}: must be non-empty string list"
        candidates = case.get("answer_candidates")
        if not isinstance(candidates, dict):
            yield f"{case_path / 'answer_candidates'}: must be an object"
        else:
            yield from _unknown_fields(candidates, CANDIDATE_FIELDS, case_path / "answer_candidates")
            yield from _missing_fields(candidates, tuple(CANDIDATE_FIELDS), case_path / "answer_candidates")
            for field in CANDIDATE_FIELDS:
                if not _string(candidates.get(field)).strip():
                    yield f"{case_path / 'answer_candidates' / field}: must be non-empty"


def _validate_input_packet(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: input_packet must be an object"
        return
    required = (
        "case_brief",
        "pre_run_failure_hypothesis",
        "critical_anchor_entities",
        "category_markers",
        "anchor_visible_candidate",
        "deck_pressure_candidate",
    )
    yield from _missing_fields(value, required, path)
    for field in ("case_brief", "pre_run_failure_hypothesis", "anchor_visible_candidate", "deck_pressure_candidate"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    for field in ("critical_anchor_entities", "category_markers"):
        if not _non_empty_string_list(value.get(field)):
            yield f"{path / field}: must be non-empty string list"


def _validate_step6_output(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: step6_output must be an object"
        return
    yield from _unknown_fields(value, STEP6_OUTPUT_FIELDS, path)
    yield from _missing_fields(value, tuple(STEP6_OUTPUT_FIELDS), path)
    if any(field not in value for field in STEP6_OUTPUT_FIELDS):
        return
    answer = _string(value.get("answer_core"))
    if not answer.strip():
        yield f"{path / 'answer_core'}: must be non-empty"
    else:
        try:
            validate_public_answer_hygiene(answer)
        except ValueError as exc:
            yield f"{path / 'answer_core'}: {exc}"
    yield from _validate_ledger(value.get("private_visibility_ledger"), path / "private_visibility_ledger")


def _validate_ledger(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: private_visibility_ledger must be a list"
        return
    ids = [_string(item.get("source_id")) if isinstance(item, dict) else "" for item in value]
    if tuple(ids) != SOURCE_IDS:
        yield f"{path}: ledger must account for anchor_visible_candidate and deck_pressure_candidate"
    for index, item in enumerate(value):
        item_path = path / f"[{index}]"
        if not isinstance(item, dict):
            yield f"{item_path}: ledger item must be an object"
            continue
        yield from _unknown_fields(item, LEDGER_FIELDS, item_path)
        yield from _missing_fields(item, tuple(LEDGER_FIELDS), item_path)
        if _string(item.get("source_id")) not in SOURCE_IDS:
            yield f"{item_path / 'source_id'}: unknown source_id"
        if _string(item.get("novelty_role")) not in {
            "visible_backbone",
            "additive_pressure",
            "confirming_support",
            "private_guardrail",
        }:
            yield f"{item_path / 'novelty_role'}: unknown novelty_role"
        if _string(item.get("disposition")) not in {
            "used",
            "combined",
            "rejected",
            "deferred",
            "private_guardrail",
        }:
            yield f"{item_path / 'disposition'}: unknown disposition"
        for field in ("why", "visible_effect"):
            if not _string(item.get(field)).strip():
                yield f"{item_path / field}: must be non-empty"


def _validate_marker_entity_detection(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: marker_entity_detection must be an object"
        return
    required = (
        "markers_present",
        "anchor_entities_missing",
        "failure_shape_observed",
        "present_markers",
        "missing_entities",
    )
    yield from _missing_fields(value, required, path)
    for field in ("markers_present", "anchor_entities_missing", "failure_shape_observed"):
        if not isinstance(value.get(field), bool):
            yield f"{path / field}: must be boolean"
    for field in ("present_markers", "missing_entities"):
        if not isinstance(value.get(field), list):
            yield f"{path / field}: must be list"


def _validate_provider_metadata(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: provider_metadata must be an object"
        return
    if "provider" not in value and "provider_name" not in value:
        yield f"{path}: provider or provider_name is required"
    if not _string(value.get("model")).strip():
        yield f"{path / 'model'}: must be non-empty"
    if not _string(value.get("status")).strip():
        yield f"{path / 'status'}: must be non-empty"


class _BlindMapResult:
    def __init__(self, value: dict[str, str], errors: list[str]) -> None:
        self.value = value
        self.errors = errors


def _validate_blind_map(value: object, path: Path) -> _BlindMapResult:
    errors: list[str] = []
    if not isinstance(value, dict):
        return _BlindMapResult({}, [f"{path}: blind_map must be an object"])
    blind_map = {str(key): _string(item) for key, item in value.items()}
    if set(blind_map) != {"A", "B"}:
        errors.append(f"{path}: blind_map must contain A and B")
    if set(blind_map.values()) != {"anchor_visible", "deck_visible"}:
        errors.append(f"{path}: blind_map must map to anchor_visible and deck_visible")
    return _BlindMapResult(blind_map, errors)


def _validate_reviewer_output(
    value: object,
    *,
    blind_map: dict[str, str],
    path: Path,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: reviewer_output must be an object"
        return
    yield from _unknown_fields(value, REVIEWER_OUTPUT_FIELDS, path)
    yield from _missing_fields(value, tuple(REVIEWER_OUTPUT_FIELDS), path)
    if any(field not in value for field in REVIEWER_OUTPUT_FIELDS):
        return
    if _string(value.get("visibility_label")) not in ALLOWED_VISIBILITY_LABELS:
        yield f"{path / 'visibility_label'}: unknown visibility_label"
    winner = _string(value.get("winner_label"))
    if winner != "tie" and winner not in blind_map:
        yield f"{path / 'winner_label'}: must be A, B, or tie"
    if _string(value.get("confidence")) not in {"high", "medium", "low"}:
        yield f"{path / 'confidence'}: unknown confidence"
    if not _string(value.get("rationale")).strip():
        yield f"{path / 'rationale'}: must be non-empty"
    if not _non_empty_string_list(value.get("anchor_entity_loss")):
        yield f"{path / 'anchor_entity_loss'}: must be non-empty string list"
    if _string(value.get("category_marker_read")) not in {"preserved", "not_preserved", "unclear"}:
        yield f"{path / 'category_marker_read'}: unknown category_marker_read"
    if _string(value.get("non_inferiority_read")) not in {"better", "non_inferior", "worse", "unclear"}:
        yield f"{path / 'non_inferiority_read'}: unknown non_inferiority_read"


def _validate_attempt_result(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: attempt result must be an object"
        return
    yield from _unknown_fields(value, ATTEMPT_RESULT_FIELDS, path)
    yield from _missing_fields(value, tuple(ATTEMPT_RESULT_FIELDS), path)
    if any(field not in value for field in ATTEMPT_RESULT_FIELDS):
        return
    if not _string(value.get("attempt_id")).strip():
        yield f"{path / 'attempt_id'}: must be non-empty"
    if _string(value.get("step6_ledger_signal")) not in ALLOWED_LEDGER_SIGNALS:
        yield f"{path / 'step6_ledger_signal'}: unknown signal"
    if _string(value.get("construction_label")) not in ALLOWED_CONSTRUCTION_LABELS:
        yield f"{path / 'construction_label'}: unknown construction_label"
    for field in ("missing_anchor_entities", "present_category_markers", "reviewer_model_families", "visibility_labels"):
        if not isinstance(value.get(field), list):
            yield f"{path / field}: must be list"
    if not isinstance(value.get("reviewer_count"), int):
        yield f"{path / 'reviewer_count'}: must be int"
    if _string(value.get("confirmed_label")) not in ALLOWED_CONFIRMED_LABELS:
        yield f"{path / 'confirmed_label'}: unknown confirmed_label"
    if not isinstance(value.get("stop_condition_triggered"), bool):
        yield f"{path / 'stop_condition_triggered'}: must be boolean"


def _validate_gates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: gates must be an object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, tuple(GATE_FIELDS), path)
    if value.get("runtime_wiring_allowed") is not False:
        yield f"{path / 'runtime_wiring_allowed'}: must be false"
    if value.get("skill_update_allowed") is not False:
        yield f"{path / 'skill_update_allowed'}: must be false"


def _reviewer_system_prompt() -> str:
    return (
        "You are a blind reviewer for a research-only visibility probe. You do not "
        "select runtime behavior. Judge only whether the visible deck-aware answer "
        "is a false positive because it drops concrete anchor entities while keeping "
        "category markers. Return strict JSON only."
    )


def _provider_metadata_dict(metadata: object) -> dict[str, object]:
    if dataclasses.is_dataclass(metadata):
        result = dataclasses.asdict(metadata)
    elif isinstance(metadata, dict):
        result = dict(metadata)
    else:
        result = {}
    if "provider_name" in result and "provider" not in result:
        result["provider"] = result["provider_name"]
    return result


def _model_family(model: str) -> str:
    return model.split("/", 1)[0] if "/" in model else model.split("-", 1)[0]


def _load_env_file(path: Path) -> None:
    if not path.exists():
        raise MarkerEntityLossFollowupError(f"env file missing: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _contains_phrase(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    normalized_text = _normalize_for_match(text)
    normalized_phrase = _normalize_for_match(phrase)
    if not normalized_phrase:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(normalized_phrase)}(?![a-z0-9])", normalized_text) is not None


def _normalize_for_match(value: str) -> str:
    value = value.casefold()
    value = value.replace("-", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _unknown_fields(payload: dict[str, object], allowed: frozenset[str], path: Path) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(payload: dict[str, object], required: Sequence[str], path: Path) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path / field}: missing required field"


def _non_empty_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def _string_list(value: object, *, fallback: str) -> list[str]:
    if isinstance(value, list):
        items = [item for item in value if isinstance(item, str) and item.strip()]
        if items:
            return items
    return [fallback] if fallback else []


def _string_dict(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): _string(item) for key, item in value.items()}


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _parse_attempt_ids(args: argparse.Namespace, contract: dict[str, object]) -> list[str]:
    if args.all:
        cases = contract.get("attempt_cases")
        if not isinstance(cases, list):
            raise MarkerEntityLossFollowupError("attempt_cases missing")
        return [_string(case.get("attempt_id")) for case in cases if isinstance(case, dict)]
    if args.attempt_id:
        return args.attempt_id
    raise MarkerEntityLossFollowupError("provide --attempt-id or --all")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--step6-dir", type=Path, default=DEFAULT_STEP6_DIR)
    parser.add_argument("--judgment-dir", type=Path, default=DEFAULT_JUDGMENT_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_OUT_DIR / "marker-entity-loss-followup.v1.json")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--attempt-id", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--step6-model", default="openai/gpt-5.1-chat")
    parser.add_argument("--reviewer-model", action="append", default=[])
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            name = path.name
            if name.endswith("marker-entity-loss-followup.v1.json"):
                validate_marker_entity_followup_contract(load_marker_entity_followup_contract(path), path=path)
            elif name.endswith("marker-entity-step6-replay.v1.json"):
                validate_step6_replay(load_step6_replay(path), path=path)
            elif name.endswith("marker-entity-visibility-judgment.v1.json"):
                validate_visibility_judgment(load_visibility_judgment(path), path=path)
            elif name.endswith("marker-entity-loss-followup-result.v1.json"):
                validate_marker_entity_followup_result(load_marker_entity_followup_result(path), path=path)
            else:
                raise MarkerEntityLossFollowupError(f"unknown artifact type: {path}")
        return 0

    if not args.live:
        for path in write_fixture_suite(out_dir=args.out_dir):
            print(path)
        return 0

    contract = (
        load_marker_entity_followup_contract(args.contract)
        if args.contract.exists()
        else build_marker_entity_followup_contract()
    )
    attempt_ids = _parse_attempt_ids(args, contract)
    reviewer_models = args.reviewer_model or list(DEFAULT_REVIEWER_MODELS)
    step6_paths = []
    judgment_paths = []
    for attempt_id in attempt_ids:
        step6_path = run_live_step6(
            contract=contract,
            attempt_id=attempt_id,
            provider=args.provider,
            model=args.step6_model,
            env_file=args.env_file,
            out_dir=args.step6_dir,
            dry_run=args.dry_run,
        )
        if step6_path is None:
            continue
        step6_paths.append(step6_path)
        print(step6_path)
        replay = load_step6_replay(step6_path)
        if replay.get("ledger_signal") != "additive_pressure_present":
            continue
        detection = replay.get("marker_entity_detection")
        if not isinstance(detection, dict) or detection.get("failure_shape_observed") is not True:
            continue
        for reviewer_model in reviewer_models:
            judgment_path = run_live_reviewer(
                contract=contract,
                step6_replay=replay,
                provider=args.provider,
                model=reviewer_model,
                env_file=args.env_file,
                out_dir=args.judgment_dir,
                seed=DEFAULT_SEED + len(judgment_paths),
                dry_run=args.dry_run,
            )
            if judgment_path is not None:
                judgment_paths.append(judgment_path)
                print(judgment_path)
    if step6_paths:
        replays = [load_step6_replay(path) for path in step6_paths]
        judgments = [load_visibility_judgment(path) for path in judgment_paths]
        result = build_marker_entity_followup_result(
            contract=contract,
            step6_replays=replays,
            judgments=judgments,
        )
        result_path = write_marker_entity_followup_result(payload=result, out_dir=args.out_dir)
        print(result_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
