#!/usr/bin/env python3
"""Research-only false-positive visibility probe.

This probe tests the mirror risk created by the ledger-mediated visibility
redesign: Step 6 may mark deck pressure as additive, the deterministic guards
may pass, and yet the anchor may still be the better visible answer.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import random
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_raw_artifacts import validate_public_answer_hygiene


CONTRACT_SCHEMA_VERSION = "pre_step6_false_positive_visibility_probe.v1"
STEP6_SCHEMA_VERSION = "pre_step6_false_positive_step6_replay.v1"
JUDGMENT_SCHEMA_VERSION = "pre_step6_false_positive_visibility_judgment.v1"
RESULT_SCHEMA_VERSION = "pre_step6_false_positive_visibility_result.v1"
STATUS = "planned_non_promotional"
RUNTIME_POLICY = "runtime_dormant"
PROBE_ID = "false_positive_visibility_probe_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-false-positive-visibility-probe")
DEFAULT_STEP6_DIR = DEFAULT_OUT_DIR / "step6-replays"
DEFAULT_JUDGMENT_DIR = DEFAULT_OUT_DIR / "judgments"
DEFAULT_SEED = 2026052102
DEFAULT_REVIEWER_MODELS = (
    "openai/gpt-5.1-chat",
    "google/gemini-3.1-flash-lite",
)
ALLOWED_LEDGER_SIGNALS = frozenset(
    {"additive_pressure_present", "all_private_or_confirming", "missing_or_unclear"}
)
ALLOWED_VISIBILITY_LABELS = frozenset(
    {"true_visible", "false_positive_visible", "ambiguous_visibility", "not_observed"}
)
ALLOWED_WINNER_ARMS = frozenset({"anchor_visible", "deck_visible", "tie"})
ALLOWED_CONFIRMED_LABELS = frozenset(
    {
        "false_positive_visible",
        "true_visible",
        "ambiguous_visibility",
        "step6_stood_down",
        "not_observed",
    }
)
ALLOWED_PROBE_RESULTS = frozenset(
    {
        "design_review_required",
        "continue_probe_with_ambiguity",
        "continue_probe_with_not_observed",
        "continue_probe",
    }
)
SOURCE_IDS = ("anchor_visible_candidate", "deck_pressure_candidate")
DETERMINISTIC_ROLE = (
    "validate_step6_ledger_schema",
    "derive_visibility_precondition",
    "preserve_blind_review_custody",
)
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "runtime_policy",
        "probe_id",
        "status",
        "promotion_effect",
        "stop_condition",
        "confirmation_rule",
        "reviewer_rule",
        "failure_response_order",
        "case_construction_rule",
        "probe_cases",
        "gates",
        "notes",
    }
)
CONFIRMATION_FIELDS = frozenset(
    {
        "confirmed_false_positive_visible",
        "split_reviewer_outcome",
        "single_reviewer_false_positive",
        "human_spot_check_only",
    }
)
REVIEWER_RULE_FIELDS = frozenset(
    {"reviewer_count", "model_family_policy", "prompt_policy", "blind_shuffle_policy"}
)
CASE_CONSTRUCTION_FIELDS = frozenset(
    {"max_attempts_per_shape", "unconstructed_shape_result", "null_evidence_warning"}
)
CASE_FIELDS = frozenset(
    {
        "case_id",
        "shape_id",
        "selection_timing",
        "case_brief",
        "pre_run_failure_hypothesis",
        "expected_step6_signal",
        "false_positive_risk",
        "case_construction_status",
        "answer_candidates",
    }
)
CANDIDATE_FIELDS = frozenset({"anchor_visible", "deck_pressure"})
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
STEP6_FIELDS = frozenset(
    {
        "schema_version",
        "runtime_policy",
        "probe_id",
        "case_id",
        "provider_metadata",
        "input_packet",
        "step6_output",
        "ledger_signal",
        "deterministic_role",
        "gates",
        "notes",
    }
)
PROVIDER_METADATA_FIELDS = frozenset(
    {
        "provider",
        "provider_name",
        "model",
        "model_family",
        "status",
        "finish_reason",
        "raw_message_content",
        "temperature",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "cached_tokens",
        "cache_write_tokens",
        "reasoning_tokens",
        "reasoning_disabled",
        "reasoning_details_present",
    }
)
STEP6_OUTPUT_FIELDS = frozenset({"answer_core", "private_visibility_ledger"})
LEDGER_FIELDS = frozenset(
    {"source_id", "disposition", "novelty_role", "why", "visible_effect", "answer_delta"}
)
LEDGER_REQUIRED_FIELDS = frozenset(
    {"source_id", "disposition", "novelty_role", "why", "visible_effect"}
)
ANSWER_DELTA_FIELDS = frozenset(
    {
        "added_entities",
        "removed_entities",
        "reordered_sequences",
        "structural_delta",
        "reframed_emphasis",
    }
)
LEGACY_OPTIONAL_ANSWER_DELTA_FIELDS = frozenset({"structural_delta"})
CONCRETE_ANSWER_DELTA_FIELDS = (
    "added_entities",
    "removed_entities",
    "reordered_sequences",
)
STRUCTURAL_ANSWER_DELTA_FIELD = "structural_delta"
STRUCTURAL_DELTA_MARKERS = (
    "boundary",
    "condition",
    "criterion",
    "criteria",
    "deadline",
    "exit",
    "gate",
    "milestone",
    "probe",
    "revisit",
    "sequence",
    "sequencing",
    "stop",
    "test",
    "unlock",
    "window",
)
VAGUE_STRUCTURAL_DELTA_PHRASES = (
    "better framing",
    "clearer framing",
    "sharper framing",
    "structural framing",
    "structural change",
)
JUDGMENT_FIELDS = frozenset(
    {
        "schema_version",
        "runtime_policy",
        "probe_id",
        "case_id",
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
        "anchor_strengths",
        "deck_regressions_or_bloat",
        "payload_loss_or_entity_loss",
        "non_inferiority_read",
    }
)
RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "runtime_policy",
        "probe_id",
        "promotion_effect",
        "case_results",
        "probe_result",
        "gates",
        "notes",
    }
)
CASE_RESULT_FIELDS = frozenset(
    {
        "case_id",
        "step6_ledger_signal",
        "answer_delta_specificity",
        "reviewer_count",
        "reviewer_model_families",
        "visibility_labels",
        "reviewer_winner_arms",
        "reviewer_non_inferiority_reads",
        "reviewer_label_consistency",
        "confirmed_label",
        "stop_condition_triggered",
    }
)
CONFIRMED_RULE_TEXT = (
    "Two reviewer judgments label the same additive-ledger case "
    "false_positive_visible under the same rubric, fresh blind shuffles, "
    "and different model families."
)


class FalsePositiveVisibilityProbeError(ValueError):
    pass


def build_false_positive_probe_contract() -> dict[str, object]:
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "probe_id": PROBE_ID,
        "status": STATUS,
        "promotion_effect": "none_bridge_only",
        "stop_condition": (
            "Any confirmed false_positive_visible triggers design review before "
            "the ledger-mediated integration draft becomes an implementation contract."
        ),
        "confirmation_rule": {
            "confirmed_false_positive_visible": CONFIRMED_RULE_TEXT,
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
        "case_construction_rule": {
            "max_attempts_per_shape": 3,
            "unconstructed_shape_result": "not_observed",
            "null_evidence_warning": (
                "Failure to construct a natural marker-preserved/entity-lost exemplar "
                "is not evidence that the omission gate is strong enough."
            ),
        },
        "probe_cases": _probe_cases(),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only mirror probe for deck over-promotion. Selection labels "
            "are pre-registered before Step 6 and reviewer calls."
        ),
    }
    validate_false_positive_probe_contract(payload)
    return payload


def load_false_positive_probe_contract(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise FalsePositiveVisibilityProbeError(f"{path}: payload must be an object")
    return payload


def write_false_positive_probe_contract(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_false_positive_probe_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "false-positive-visibility-probe.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_false_positive_probe_contract(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_false_positive_probe_contract_errors(payload, path=Path(path)))
    if errors:
        raise FalsePositiveVisibilityProbeError("; ".join(errors))


def iter_false_positive_probe_contract_errors(
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
    if payload.get("probe_id") != PROBE_ID:
        yield f"{path / 'probe_id'}: must be {PROBE_ID}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("promotion_effect") != "none_bridge_only":
        yield f"{path / 'promotion_effect'}: must be none_bridge_only"
    if not _string(payload.get("stop_condition")).startswith("Any confirmed false_positive_visible"):
        yield f"{path / 'stop_condition'}: must be consequential"
    yield from _validate_confirmation_rule(payload.get("confirmation_rule"), path / "confirmation_rule")
    yield from _validate_reviewer_rule(payload.get("reviewer_rule"), path / "reviewer_rule")
    if payload.get("failure_response_order") != [
        "tighten_answer_delta_visible_effect_check",
        "add_entity_level_payload_gate",
        "split_additive_private_pressure_from_additive_public_payload",
    ]:
        yield f"{path / 'failure_response_order'}: invalid failure-response order"
    yield from _validate_case_construction_rule(
        payload.get("case_construction_rule"),
        path / "case_construction_rule",
    )
    yield from _validate_probe_cases(payload.get("probe_cases"), path / "probe_cases")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def build_step6_replay_prompts(
    *,
    contract: dict[str, object],
    case_id: str,
) -> dict[str, str]:
    validate_false_positive_probe_contract(contract)
    case = _case_by_id(contract, case_id)
    candidates = _answer_candidates(case, case_id)
    system_prompt = (
        "You are Step 6, the primary reasoning voice. You will receive an anchor "
        "candidate and a private deck-pressure candidate. Decide the best public "
        "answer and record a private ledger. Return strict JSON only."
    )
    user_prompt = "\n\n".join(
        [
            "FALSE-POSITIVE VISIBILITY PROBE CONTEXT",
            json.dumps(
                {
                    "case_id": case_id,
                    "case_brief": case["case_brief"],
                    "pre_run_failure_hypothesis": case["pre_run_failure_hypothesis"],
                    "false_positive_risk": case["false_positive_risk"],
                    "anchor_visible_candidate": candidates["anchor_visible"],
                    "deck_pressure_candidate": candidates["deck_pressure"],
                },
                indent=2,
                ensure_ascii=False,
            ),
            "TASK",
            (
                "Write the best public-clean answer_core. Use the deck-pressure "
                "candidate only if it adds concrete decision value; keep it private "
                "or confirming if it is merely clever, abstract, redundant, or true "
                "but not useful. Preserve named resources, actor sequence, dates or "
                "windows, evidence checks, and specific entities from the anchor when "
                "they matter. Do not expose private labels. The ledger must honestly "
                "record whether the deck pressure was additive public value or only "
                "private/confirming thought. If the deck changes the visible answer "
                "through a specific stop condition, unlock condition, decision boundary, "
                "test design, or commitment boundary, record that in structural_delta. "
                "Do not use vague structural_delta entries like 'added structural framing'."
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
                            "answer_delta": {
                                "added_entities": ["Concrete entities added to the visible answer."],
                                "removed_entities": ["Concrete anchor entities removed, if any."],
                                "reordered_sequences": ["Concrete sequence/order changes, if any."],
                                "structural_delta": [
                                    (
                                        "Specific structural change such as a stop condition, "
                                        "unlock condition, decision boundary, test design, "
                                        "or commitment boundary."
                                    )
                                ],
                                "reframed_emphasis": ["Abstract emphasis shifts, if any."],
                            },
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
) -> dict[str, object]:
    validate_false_positive_probe_contract(contract)
    case = _case_by_id(contract, case_id)
    candidates = _answer_candidates(case, case_id)
    deck_role = (
        "additive_pressure"
        if ledger_signal == "additive_pressure_present"
        else "confirming_support"
    )
    deck_disposition = "combined" if ledger_signal == "additive_pressure_present" else "deferred"
    step6_output = {
        "answer_core": (
            _string(candidates["deck_pressure"])
            if ledger_signal == "additive_pressure_present"
            else _string(candidates["anchor_visible"])
        ),
        "private_visibility_ledger": [
            {
                "source_id": "anchor_visible_candidate",
                "disposition": "used",
                "novelty_role": "visible_backbone",
                "why": "Anchor supplied the concrete baseline.",
                "visible_effect": "Kept the baseline answer available.",
                "answer_delta": {
                    "added_entities": [],
                    "removed_entities": [],
                    "reordered_sequences": [],
                    "structural_delta": [],
                    "reframed_emphasis": [],
                },
            },
            {
                "source_id": "deck_pressure_candidate",
                "disposition": deck_disposition,
                "novelty_role": deck_role,
                "why": "Static fixture for false-positive visibility probe.",
                "visible_effect": "Added deck-pressure framing." if deck_role == "additive_pressure" else "none",
                "answer_delta": {
                    "added_entities": ["deck-pressure candidate"] if deck_role == "additive_pressure" else [],
                    "removed_entities": [],
                    "reordered_sequences": [],
                    "structural_delta": [],
                    "reframed_emphasis": ["deck-pressure framing"] if deck_role == "additive_pressure" else [],
                },
            },
        ],
    }
    payload = {
        "schema_version": STEP6_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "probe_id": PROBE_ID,
        "case_id": case_id,
        "provider_metadata": {
            "provider": "static",
            "model": "static-step6-fixture",
            "model_family": "static",
            "status": "ok",
        },
        "input_packet": _input_packet(case, candidates),
        "step6_output": step6_output,
        "ledger_signal": derive_ledger_signal(step6_output),
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
        raise FalsePositiveVisibilityProbeError(f"{path}: payload must be an object")
    return payload


def write_step6_replay(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_step6_replay(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{_string(payload['case_id'])}.false-positive-step6-replay.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_step6_replay(payload: dict[str, object], *, path: Path = Path("<payload>")) -> None:
    errors = list(iter_step6_replay_errors(payload, path=Path(path)))
    if errors:
        raise FalsePositiveVisibilityProbeError("; ".join(errors))


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
    if payload.get("probe_id") != PROBE_ID:
        yield f"{path / 'probe_id'}: must be {PROBE_ID}"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    yield from _validate_provider_metadata(payload.get("provider_metadata"), path / "provider_metadata")
    yield from _validate_input_packet(payload.get("input_packet"), path / "input_packet")
    step6_output = payload.get("step6_output")
    yield from _validate_step6_output(step6_output, path / "step6_output")
    expected_signal = derive_ledger_signal(step6_output)
    if payload.get("ledger_signal") != expected_signal:
        yield f"{path / 'ledger_signal'}: must be derived from Step 6 ledger"
    if payload.get("deterministic_role") != list(DETERMINISTIC_ROLE):
        yield f"{path / 'deterministic_role'}: invalid deterministic role"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def build_reviewer_packet(
    *,
    contract: dict[str, object],
    step6_replay: dict[str, object],
    seed: int = DEFAULT_SEED,
) -> dict[str, object]:
    validate_false_positive_probe_contract(contract)
    validate_step6_replay(step6_replay)
    case_id = _string(step6_replay["case_id"])
    case = _case_by_id(contract, case_id)
    candidates = _answer_candidates(case, case_id)
    arms = ["anchor_visible", "deck_visible"]
    rng = random.Random(seed + sum(ord(char) for char in case_id))
    rng.shuffle(arms)
    blind_map = dict(zip(("A", "B"), arms, strict=True))
    answer_by_arm = {
        "anchor_visible": _string(candidates["anchor_visible"]),
        "deck_visible": _string(step6_replay["step6_output"]["answer_core"]),
    }
    return {
        "probe_id": PROBE_ID,
        "case_id": case_id,
        "case_brief": case["case_brief"],
        "pre_run_failure_hypothesis": case["pre_run_failure_hypothesis"],
        "false_positive_risk": case["false_positive_risk"],
        "policy_precondition": {
            "step6_ledger_signal": step6_replay["ledger_signal"],
            "visibility_policy_would_surface_deck": (
                step6_replay["ledger_signal"] == "additive_pressure_present"
            ),
        },
        "reviewer_task": (
            "Compare two candidate visible answers. The runtime policy would surface "
            "the deck-aware answer only because Step 6 marked deck pressure additive. "
            "Label false_positive_visible if the anchor is materially better and the "
            "deck-aware answer should not have been visible. Label true_visible if "
            "the deck-aware answer is better or non-inferior. Label ambiguous_visibility "
            "if mixed. Label not_observed if the packet cannot test the failure mode."
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
            "anchor_strengths": ["Concrete anchor strengths, if any."],
            "deck_regressions_or_bloat": ["Deck regressions, if any."],
            "payload_loss_or_entity_loss": ["Specific missing entities, if any."],
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
        "probe_id": PROBE_ID,
        "case_id": _string(step6_replay["case_id"]),
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
            "anchor_strengths": ["Static anchor strength."],
            "deck_regressions_or_bloat": ["Static deck regression."],
            "payload_loss_or_entity_loss": ["none"],
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
        raise FalsePositiveVisibilityProbeError(f"{path}: payload must be an object")
    return payload


def write_visibility_judgment(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_visibility_judgment(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = _string(payload["provider_metadata"]["model"]).replace("/", "__")
    path = out_dir / f"{_string(payload['case_id'])}.{model_slug}.false-positive-visibility-judgment.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_visibility_judgment(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_visibility_judgment_errors(payload, path=Path(path)))
    if errors:
        raise FalsePositiveVisibilityProbeError("; ".join(errors))


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
    if payload.get("probe_id") != PROBE_ID:
        yield f"{path / 'probe_id'}: must be {PROBE_ID}"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    yield from _validate_provider_metadata(payload.get("provider_metadata"), path / "provider_metadata")
    blind_map = _validate_blind_map(payload.get("blind_map"), path / "blind_map")
    yield from blind_map.errors
    yield from _validate_reviewer_output(
        payload.get("reviewer_output"),
        blind_map=blind_map.value,
        path=path / "reviewer_output",
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def build_false_positive_probe_result(
    *,
    contract: dict[str, object],
    step6_replays: Sequence[dict[str, object]],
    judgments: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_false_positive_probe_contract(contract)
    for replay in step6_replays:
        validate_step6_replay(replay)
    for judgment in judgments:
        validate_visibility_judgment(judgment)
    judgments_by_case: dict[str, list[dict[str, object]]] = {}
    for judgment in judgments:
        judgments_by_case.setdefault(_string(judgment["case_id"]), []).append(judgment)
    case_results = []
    for replay in sorted(step6_replays, key=lambda item: _string(item["case_id"])):
        case_id = _string(replay["case_id"])
        case = _case_by_id(contract, case_id)
        ledger_signal = _string(replay["ledger_signal"])
        case_judgments = judgments_by_case.get(case_id, [])
        labels = [_string(judgment["reviewer_output"]["visibility_label"]) for judgment in case_judgments]
        winner_arms = [_reviewer_winner_arm(judgment) for judgment in case_judgments]
        non_inferiority_reads = [
            _string(judgment["reviewer_output"]["non_inferiority_read"])
            for judgment in case_judgments
        ]
        families = sorted(
            {
                _string(judgment["provider_metadata"].get("model_family"))
                for judgment in case_judgments
                if _string(judgment["provider_metadata"].get("model_family"))
            }
        )
        label_consistency = _reviewer_label_consistency(
            labels=labels,
            winner_arms=winner_arms,
            non_inferiority_reads=non_inferiority_reads,
        )
        raw_confirmed = _confirmed_label(
            ledger_signal=ledger_signal,
            labels=labels,
            families=families,
            shape_id=_string(case.get("shape_id")),
        )
        confirmed = (
            "ambiguous_visibility"
            if raw_confirmed == "true_visible" and label_consistency == "tension_detected"
            else raw_confirmed
        )
        case_results.append(
            {
                "case_id": case_id,
                "step6_ledger_signal": ledger_signal,
                "answer_delta_specificity": derive_answer_delta_specificity(
                    replay.get("step6_output")
                ),
                "reviewer_count": len(case_judgments),
                "reviewer_model_families": families,
                "visibility_labels": labels,
                "reviewer_winner_arms": winner_arms,
                "reviewer_non_inferiority_reads": non_inferiority_reads,
                "reviewer_label_consistency": label_consistency,
                "confirmed_label": confirmed,
                "stop_condition_triggered": confirmed == "false_positive_visible",
            }
        )
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "probe_id": PROBE_ID,
        "promotion_effect": "none_bridge_only",
        "case_results": case_results,
        "probe_result": _probe_result(case_results),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Aggregate result for non-promotional false-positive visibility probe.",
    }
    validate_false_positive_probe_result(payload)
    return payload


def load_false_positive_probe_result(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise FalsePositiveVisibilityProbeError(f"{path}: payload must be an object")
    return payload


def write_false_positive_probe_result(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_false_positive_probe_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "false-positive-visibility-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_false_positive_probe_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_false_positive_probe_result_errors(payload, path=Path(path)))
    if errors:
        raise FalsePositiveVisibilityProbeError("; ".join(errors))


def iter_false_positive_probe_result_errors(
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
    if payload.get("probe_id") != PROBE_ID:
        yield f"{path / 'probe_id'}: must be {PROBE_ID}"
    if payload.get("promotion_effect") != "none_bridge_only":
        yield f"{path / 'promotion_effect'}: must be none_bridge_only"
    results = payload.get("case_results")
    if not isinstance(results, list):
        yield f"{path / 'case_results'}: must be a list"
    else:
        for index, result in enumerate(results):
            yield from _validate_case_result(result, path / "case_results" / str(index))
        expected = _probe_result(results)
        if payload.get("probe_result") != expected:
            yield f"{path / 'probe_result'}: must be {expected}"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def run_live_step6(
    *,
    contract: dict[str, object],
    case_id: str,
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
    prompts = build_step6_replay_prompts(contract=contract, case_id=case_id)
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
        stage="pre_step6_false_positive_step6_replay",
        tendency_id=case_id,
    )
    provider_metadata = _provider_metadata_dict(metadata)
    provider_metadata["model_family"] = _model_family(_string(provider_metadata.get("model")))
    if _string(provider_metadata.get("status")) != "ok":
        raise FalsePositiveVisibilityProbeError(
            "live false-positive Step 6 replay failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    case = _case_by_id(contract, case_id)
    candidates = _answer_candidates(case, case_id)
    step6_output = _normalize_step6_output(output)
    payload = {
        "schema_version": STEP6_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "probe_id": PROBE_ID,
        "case_id": case_id,
        "provider_metadata": provider_metadata,
        "input_packet": _input_packet(case, candidates),
        "step6_output": step6_output,
        "ledger_signal": derive_ledger_signal(step6_output),
        "deterministic_role": list(DETERMINISTIC_ROLE),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Live Step 6 replay for false-positive visibility probe.",
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
        stage="pre_step6_false_positive_visibility_probe",
        tendency_id=_string(step6_replay["case_id"]),
    )
    provider_metadata = _provider_metadata_dict(metadata)
    provider_metadata["model_family"] = _model_family(_string(provider_metadata.get("model")))
    if _string(provider_metadata.get("status")) != "ok":
        raise FalsePositiveVisibilityProbeError(
            "live false-positive visibility probe failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "probe_id": PROBE_ID,
        "case_id": _string(step6_replay["case_id"]),
        "judgment_source": "manual_llm_reviewer_judgment",
        "provider_metadata": provider_metadata,
        "blind_map": private_blind_map,
        "reviewer_output": _normalize_reviewer_output(output, blind_map=private_blind_map),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Live visibility judgment for false-positive probe.",
    }
    return write_visibility_judgment(payload=payload, out_dir=out_dir)


def write_fixture_suite(*, out_dir: Path) -> list[Path]:
    contract = build_false_positive_probe_contract()
    return [write_false_positive_probe_contract(payload=contract, out_dir=out_dir)]


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


def derive_answer_delta_specificity(step6_output: object) -> str:
    if not isinstance(step6_output, dict):
        return "missing_or_unclear"
    ledger = step6_output.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        return "missing_or_unclear"
    additive_items = [
        item
        for item in ledger
        if isinstance(item, dict)
        and item.get("source_id") == "deck_pressure_candidate"
        and item.get("novelty_role") == "additive_pressure"
        and item.get("disposition") in {"used", "combined"}
    ]
    if not additive_items:
        return "not_applicable"
    saw_reframe = False
    for item in additive_items:
        delta = item.get("answer_delta")
        if not isinstance(delta, dict):
            continue
        if any(_non_empty_string_list(delta.get(field)) for field in CONCRETE_ANSWER_DELTA_FIELDS):
            return "concrete_delta_present"
        if _specific_structural_delta_present(delta.get(STRUCTURAL_ANSWER_DELTA_FIELD)):
            return "structural_delta_present"
        if _non_empty_string_list(delta.get("reframed_emphasis")):
            saw_reframe = True
    if saw_reframe:
        return "reframe_only"
    return "missing_or_unclear"


def _probe_cases() -> list[dict[str, object]]:
    return [
        {
            "case_id": "fp-bevelin-irrelevant-incentives",
            "shape_id": "bevelin_structurally_applicable_but_irrelevant",
            "selection_timing": "pre_run",
            "case_brief": (
                "User needs a short client follow-up after a normal status meeting. "
                "The useful answer is a concrete message, not a theory of incentives."
            ),
            "pre_run_failure_hypothesis": (
                "If Step 6 marks incentive pressure additive and surfaces a deck-aware "
                "answer that is more abstract than the concrete client follow-up, this "
                "is a false positive."
            ),
            "expected_step6_signal": "additive_pressure_present",
            "false_positive_risk": [
                "Bevelin-style incentive framing is structurally available but irrelevant.",
                "The deck answer may sound wiser while making the email less usable.",
            ],
            "case_construction_status": "candidate_exemplar",
            "answer_candidates": {
                "anchor_visible": (
                    "Send a short note today: 'Thanks for the discussion. I will send "
                    "the revised timeline by Thursday, flag the two open assumptions, "
                    "and confirm whether the finance input changes the launch date.'"
                ),
                "deck_pressure": (
                    "Before replying, consider the incentive map: the client may reward "
                    "confidence but punish hidden uncertainty, finance may be protecting "
                    "its own deadline, and your safest move is to avoid false precision. "
                    "Name incentives, uncertainty, and decision ownership in the follow-up."
                ),
            },
        },
        {
            "case_id": "fp-polya-true-but-useless",
            "shape_id": "polya_true_but_useless_abstraction",
            "selection_timing": "pre_run",
            "case_brief": (
                "User already has a clean Wednesday protocol for asking counsel about "
                "a report boundary. The risk is replacing it with generic problem-shape advice."
            ),
            "pre_run_failure_hypothesis": (
                "If Step 6 marks Polya problem-shape pressure additive and surfaces "
                "an answer that weakens the concrete Wednesday protocol, this is a "
                "false positive."
            ),
            "expected_step6_signal": "additive_pressure_present",
            "false_positive_risk": [
                "Polya knowns/unknowns framing is true but less useful than the existing sequence.",
                "The deck answer may remove the named Wednesday step and counsel-first boundary.",
            ],
            "case_construction_status": "candidate_exemplar",
            "answer_candidates": {
                "anchor_visible": (
                    "On Wednesday, send counsel the two paragraphs and ask one narrow "
                    "question: 'Does this create a legal or client-confidentiality issue "
                    "if I include it in the report?' Do not broaden the debate until "
                    "counsel answers that question."
                ),
                "deck_pressure": (
                    "First clarify the problem type. Separate what is known, unknown, "
                    "and controllable; identify the invariant constraint; then choose "
                    "the next informative move that reduces uncertainty before committing "
                    "to the report wording."
                ),
            },
        },
        {
            "case_id": "fp-marker-preserved-entity-lost",
            "shape_id": "marker_preserved_entity_lost",
            "selection_timing": "pre_run",
            "case_brief": (
                "Sensitive parent/minor case where the anchor contains named resources "
                "and concrete tripwire entities. The probe tests marker preservation "
                "while specific entities disappear."
            ),
            "pre_run_failure_hypothesis": (
                "If Step 6 marks generalized safety framing additive while the answer "
                "keeps category markers but drops RAINN, counsel, meeting requests, "
                "sexual images, threats, and hidden-channel migration, this is a false positive."
            ),
            "expected_step6_signal": "additive_pressure_present",
            "false_positive_risk": [
                "Omission gate may see resources and tripwires as present by marker.",
                "Specific resources and tripwire entities may be lost inside those categories.",
            ],
            "case_construction_status": "candidate_exemplar",
            "answer_candidates": {
                "anchor_visible": (
                    "Talk with RAINN, a therapist, or counsel before deciding whether "
                    "to report. Keep the phone channel open unless a concrete tripwire "
                    "fires: a request to meet, sexual images, threats, evidence of other "
                    "minors, migration to hidden channels, or your daughter saying she "
                    "feels pressured or afraid."
                ),
                "deck_pressure": (
                    "Use a safety-first plan with professional support. Keep trust central, "
                    "monitor for concerning signals, preserve communication boundaries, "
                    "and escalate if the situation becomes more dangerous. Do not treat "
                    "quiet behavior as proof that risk has disappeared."
                ),
            },
        },
    ]


def _case_by_id(contract: dict[str, object], case_id: str) -> dict[str, object]:
    cases = contract.get("probe_cases")
    if not isinstance(cases, list):
        raise FalsePositiveVisibilityProbeError("probe_cases missing")
    for case in cases:
        if isinstance(case, dict) and case.get("case_id") == case_id:
            return case
    raise FalsePositiveVisibilityProbeError(f"unknown probe case: {case_id}")


def _answer_candidates(case: dict[str, object], case_id: str) -> dict[str, object]:
    candidates = case.get("answer_candidates")
    if not isinstance(candidates, dict):
        raise FalsePositiveVisibilityProbeError(f"{case_id}: answer_candidates missing")
    for arm in ("anchor_visible", "deck_pressure"):
        if not _string(candidates.get(arm)).strip():
            raise FalsePositiveVisibilityProbeError(f"{case_id}: {arm} missing")
    return candidates


def _input_packet(case: dict[str, object], candidates: dict[str, object]) -> dict[str, object]:
    return {
        "case_brief": case["case_brief"],
        "pre_run_failure_hypothesis": case["pre_run_failure_hypothesis"],
        "false_positive_risk": case["false_positive_risk"],
        "anchor_visible_candidate": candidates["anchor_visible"],
        "deck_pressure_candidate": candidates["deck_pressure"],
    }


def _confirmed_label(
    *,
    ledger_signal: str,
    labels: list[str],
    families: list[str],
    shape_id: str,
) -> str:
    if ledger_signal != "additive_pressure_present":
        if shape_id == "marker_preserved_entity_lost":
            return "not_observed"
        return "step6_stood_down"
    if len(families) < 2 or len(labels) < 2:
        return "not_observed"
    if labels.count("false_positive_visible") == len(labels):
        return "false_positive_visible"
    if labels.count("true_visible") == len(labels):
        return "true_visible"
    if "not_observed" in labels:
        return "not_observed"
    return "ambiguous_visibility"


def _reviewer_winner_arm(judgment: dict[str, object]) -> str:
    blind_map = _string_dict(judgment.get("blind_map"))
    reviewer_output = judgment.get("reviewer_output")
    if not isinstance(reviewer_output, dict):
        return "unknown"
    winner = _string(reviewer_output.get("winner_label"))
    if winner == "tie":
        return "tie"
    return blind_map.get(winner, "unknown")


def _reviewer_label_consistency(
    *,
    labels: Sequence[str],
    winner_arms: Sequence[str],
    non_inferiority_reads: Sequence[str],
) -> str:
    if not labels:
        return "not_applicable"
    for label, winner_arm, non_inferiority in zip(
        labels,
        winner_arms,
        non_inferiority_reads,
        strict=False,
    ):
        if label == "false_positive_visible" and winner_arm != "anchor_visible":
            return "tension_detected"
        if (
            label == "true_visible"
            and winner_arm == "anchor_visible"
            and non_inferiority != "non_inferior"
        ):
            return "tension_detected"
    return "aligned"


def _probe_result(case_results: Sequence[object]) -> str:
    if any(
        isinstance(result, dict) and result.get("stop_condition_triggered") is True
        for result in case_results
    ):
        return "design_review_required"
    if any(
        isinstance(result, dict) and result.get("confirmed_label") == "ambiguous_visibility"
        for result in case_results
    ):
        return "continue_probe_with_ambiguity"
    if any(
        isinstance(result, dict) and result.get("confirmed_label") == "not_observed"
        for result in case_results
    ):
        return "continue_probe_with_not_observed"
    return "continue_probe"


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
        normalized.append(
            {
                "source_id": source_id,
                "disposition": _string(item.get("disposition")) or "deferred",
                "novelty_role": _string(item.get("novelty_role"))
                or (
                    "visible_backbone"
                    if source_id == "anchor_visible_candidate"
                    else "confirming_support"
                ),
                "why": _string(item.get("why")) or "Model did not explain this source.",
                "visible_effect": _string(item.get("visible_effect")) or "none",
                "answer_delta": _normalize_answer_delta(item.get("answer_delta")),
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
    return {
        "visibility_label": label,
        "winner_label": winner,
        "confidence": confidence,
        "rationale": _string(value.get("rationale")) or "Reviewer did not provide rationale.",
        "anchor_strengths": _string_list(value.get("anchor_strengths"), fallback="none"),
        "deck_regressions_or_bloat": _string_list(
            value.get("deck_regressions_or_bloat"),
            fallback="none",
        ),
        "payload_loss_or_entity_loss": _string_list(
            value.get("payload_loss_or_entity_loss"),
            fallback="none",
        ),
        "non_inferiority_read": _string(value.get("non_inferiority_read")) or "unclear",
    }


def _normalize_answer_delta(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        value = {}
    return {
        field: _string_list(value.get(field), fallback="")
        if _string_list(value.get(field), fallback="")
        != [""]
        else []
        for field in sorted(ANSWER_DELTA_FIELDS)
    }


def _specific_structural_delta_present(value: object) -> bool:
    if not isinstance(value, list):
        return False
    return any(_is_specific_structural_delta(item) for item in value)


def _is_specific_structural_delta(value: object) -> bool:
    if not isinstance(value, str):
        return False
    text = " ".join(value.lower().split())
    if not text:
        return False
    words = [word.strip(".,:;()[]{}!?") for word in text.split()]
    marker_present = any(marker in text for marker in STRUCTURAL_DELTA_MARKERS)
    if len(words) < 5 or not marker_present:
        return False
    return not any(text == phrase or text.endswith(f" {phrase}") for phrase in VAGUE_STRUCTURAL_DELTA_PHRASES)


def _validate_confirmation_rule(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: confirmation_rule must be an object"
        return
    yield from _unknown_fields(value, CONFIRMATION_FIELDS, path)
    yield from _missing_fields(value, tuple(CONFIRMATION_FIELDS), path)
    if value.get("confirmed_false_positive_visible") != CONFIRMED_RULE_TEXT:
        yield f"{path / 'confirmed_false_positive_visible'}: invalid rule"
    if value.get("split_reviewer_outcome") != "ambiguous_visibility":
        yield f"{path / 'split_reviewer_outcome'}: must be ambiguous_visibility"


def _validate_reviewer_rule(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: reviewer_rule must be an object"
        return
    yield from _unknown_fields(value, REVIEWER_RULE_FIELDS, path)
    yield from _missing_fields(value, tuple(REVIEWER_RULE_FIELDS), path)
    if value.get("reviewer_count") != 2:
        yield f"{path / 'reviewer_count'}: must be 2"
    if value.get("model_family_policy") != "different_model_family_required":
        yield f"{path / 'model_family_policy'}: must require different families"


def _validate_case_construction_rule(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: case_construction_rule must be an object"
        return
    yield from _unknown_fields(value, CASE_CONSTRUCTION_FIELDS, path)
    yield from _missing_fields(value, tuple(CASE_CONSTRUCTION_FIELDS), path)
    if value.get("max_attempts_per_shape") != 3:
        yield f"{path / 'max_attempts_per_shape'}: must be 3"
    if value.get("unconstructed_shape_result") != "not_observed":
        yield f"{path / 'unconstructed_shape_result'}: must be not_observed"
    if "not evidence" not in _string(value.get("null_evidence_warning")):
        yield f"{path / 'null_evidence_warning'}: must warn about null evidence"


def _validate_probe_cases(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list) or len(value) != 3:
        yield f"{path}: probe_cases must contain exactly 3 cases"
        return
    for index, case in enumerate(value):
        case_path = path / str(index)
        if not isinstance(case, dict):
            yield f"{case_path}: case must be an object"
            continue
        yield from _unknown_fields(case, CASE_FIELDS, case_path)
        yield from _missing_fields(case, tuple(CASE_FIELDS), case_path)
        if any(field not in case for field in CASE_FIELDS):
            continue
        if case.get("selection_timing") != "pre_run":
            yield f"{case_path / 'selection_timing'}: must be pre_run"
        if case.get("expected_step6_signal") != "additive_pressure_present":
            yield f"{case_path / 'expected_step6_signal'}: must be additive_pressure_present"
        if case.get("case_construction_status") not in {"candidate_exemplar", "not_observed"}:
            yield f"{case_path / 'case_construction_status'}: unknown status"
        if not _non_empty_string_list(case.get("false_positive_risk")):
            yield f"{case_path / 'false_positive_risk'}: must be non-empty string list"
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
        "false_positive_risk",
        "anchor_visible_candidate",
        "deck_pressure_candidate",
    )
    yield from _missing_fields(value, required, path)
    for field in ("case_brief", "pre_run_failure_hypothesis", "anchor_visible_candidate", "deck_pressure_candidate"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if not _non_empty_string_list(value.get("false_positive_risk")):
        yield f"{path / 'false_positive_risk'}: must be non-empty string list"


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
        yield from _missing_fields(item, tuple(LEDGER_REQUIRED_FIELDS), item_path)
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
        answer_delta = item.get("answer_delta")
        if answer_delta is not None:
            yield from _validate_answer_delta(answer_delta, item_path / "answer_delta")


def _validate_answer_delta(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: answer_delta must be an object"
        return
    yield from _unknown_fields(value, ANSWER_DELTA_FIELDS, path)
    yield from _missing_fields(
        value,
        tuple(ANSWER_DELTA_FIELDS - LEGACY_OPTIONAL_ANSWER_DELTA_FIELDS),
        path,
    )
    for field in ANSWER_DELTA_FIELDS:
        if not isinstance(value.get(field), list):
            yield f"{path / field}: must be a list"
            continue
        if any(not isinstance(item, str) for item in value[field]):
            yield f"{path / field}: must contain strings"


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
    for field in sorted(set(value) - PROVIDER_METADATA_FIELDS):
        yield f"{path / field}: unknown field"


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
    for field in ("anchor_strengths", "deck_regressions_or_bloat", "payload_loss_or_entity_loss"):
        if not _non_empty_string_list(value.get(field)):
            yield f"{path / field}: must be a non-empty string list"
    if _string(value.get("non_inferiority_read")) not in {"better", "non_inferior", "worse", "unclear"}:
        yield f"{path / 'non_inferiority_read'}: unknown non_inferiority_read"


def _validate_case_result(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: case result must be an object"
        return
    yield from _unknown_fields(value, CASE_RESULT_FIELDS, path)
    yield from _missing_fields(value, tuple(CASE_RESULT_FIELDS), path)
    if any(field not in value for field in CASE_RESULT_FIELDS):
        return
    if not _string(value.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    if _string(value.get("step6_ledger_signal")) not in ALLOWED_LEDGER_SIGNALS:
        yield f"{path / 'step6_ledger_signal'}: unknown signal"
    if _string(value.get("answer_delta_specificity")) not in {
        "concrete_delta_present",
        "structural_delta_present",
        "reframe_only",
        "missing_or_unclear",
        "not_applicable",
    }:
        yield f"{path / 'answer_delta_specificity'}: unknown answer_delta_specificity"
    if not isinstance(value.get("reviewer_count"), int):
        yield f"{path / 'reviewer_count'}: must be int"
    if not isinstance(value.get("reviewer_model_families"), list):
        yield f"{path / 'reviewer_model_families'}: must be list"
    if not isinstance(value.get("visibility_labels"), list):
        yield f"{path / 'visibility_labels'}: must be list"
    if not isinstance(value.get("reviewer_winner_arms"), list):
        yield f"{path / 'reviewer_winner_arms'}: must be list"
    if not isinstance(value.get("reviewer_non_inferiority_reads"), list):
        yield f"{path / 'reviewer_non_inferiority_reads'}: must be list"
    if _string(value.get("reviewer_label_consistency")) not in {
        "aligned",
        "tension_detected",
        "not_applicable",
    }:
        yield f"{path / 'reviewer_label_consistency'}: unknown consistency"
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
        "select runtime behavior. Judge whether surfacing the deck-aware answer would "
        "be a false positive. Return strict JSON only."
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
        raise FalsePositiveVisibilityProbeError(f"env file missing: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


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
    return [fallback]


def _string_dict(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): _string(item) for key, item in value.items()}


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _parse_case_ids(args: argparse.Namespace, contract: dict[str, object]) -> list[str]:
    if args.all:
        cases = contract.get("probe_cases")
        if not isinstance(cases, list):
            raise FalsePositiveVisibilityProbeError("probe_cases missing")
        return [_string(case.get("case_id")) for case in cases if isinstance(case, dict)]
    if args.case_id:
        return args.case_id
    raise FalsePositiveVisibilityProbeError("provide --case-id or --all")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--step6-dir", type=Path, default=DEFAULT_STEP6_DIR)
    parser.add_argument("--judgment-dir", type=Path, default=DEFAULT_JUDGMENT_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_OUT_DIR / "false-positive-visibility-probe.v1.json")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--step6-model", default="openai/gpt-5.1-chat")
    parser.add_argument("--reviewer-model", action="append", default=[])
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--result-only",
        action="store_true",
        help="Rebuild the aggregate result from existing replay and judgment artifacts.",
    )
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            name = path.name
            if name.endswith("false-positive-visibility-probe.v1.json"):
                validate_false_positive_probe_contract(load_false_positive_probe_contract(path), path=path)
            elif name.endswith("false-positive-step6-replay.v1.json"):
                validate_step6_replay(load_step6_replay(path), path=path)
            elif name.endswith("false-positive-visibility-judgment.v1.json"):
                validate_visibility_judgment(load_visibility_judgment(path), path=path)
            elif name.endswith("false-positive-visibility-result.v1.json"):
                validate_false_positive_probe_result(load_false_positive_probe_result(path), path=path)
            else:
                raise FalsePositiveVisibilityProbeError(f"unknown artifact type: {path}")
        return 0

    if args.result_only:
        contract = load_false_positive_probe_contract(args.contract)
        step6_paths = sorted(args.step6_dir.glob("*.false-positive-step6-replay.v1.json"))
        judgment_paths = sorted(args.judgment_dir.glob("*.false-positive-visibility-judgment.v1.json"))
        result = build_false_positive_probe_result(
            contract=contract,
            step6_replays=[load_step6_replay(path) for path in step6_paths],
            judgments=[load_visibility_judgment(path) for path in judgment_paths],
        )
        print(write_false_positive_probe_result(payload=result, out_dir=args.out_dir))
        return 0

    if not args.live:
        for path in write_fixture_suite(out_dir=args.out_dir):
            print(path)
        return 0

    contract = (
        load_false_positive_probe_contract(args.contract)
        if args.contract.exists()
        else build_false_positive_probe_contract()
    )
    case_ids = _parse_case_ids(args, contract)
    reviewer_models = args.reviewer_model or list(DEFAULT_REVIEWER_MODELS)
    step6_paths = []
    judgment_paths = []
    for case_id in case_ids:
        step6_path = run_live_step6(
            contract=contract,
            case_id=case_id,
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
        result = build_false_positive_probe_result(
            contract=contract,
            step6_replays=replays,
            judgments=judgments,
        )
        result_path = write_false_positive_probe_result(payload=result, out_dir=args.out_dir)
        print(result_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
