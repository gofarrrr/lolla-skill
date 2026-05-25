"""Dormant pre-Step-6 portfolio shadow contract.

This module intentionally does not build card decks, call reviewers, or decide
wisdom. It records whether a cached portfolio would have been eligible for a
deck-aware visible answer under the proposed policy, while leaving the real
user-visible Step 6 output untouched.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "pre_step6_shadow_portfolio.v1"
CARD_DECK_SCHEMA_VERSION = "pre_step6_card_deck.v1"
STEP6_LEDGER_SCHEMA_VERSION = "pre_step6_shadow_step6_ledger.v1"

_CACHE_FILE_SUFFIX = ".pre-step6-shadow-card-deck.v1.json"
_ANCHOR_SOURCE_IDS = {
    "anchor_visible_candidate",
    "clean_hybrid_card",
    "current_step6_anchor",
    "rendered_hybrid",
}
_PRIVATE_OR_CONFIRMING_DISPOSITIONS = {
    "deferred",
    "private_guardrail",
    "rejected",
}
_PRIVATE_OR_CONFIRMING_ROLES = {
    "confirming_support",
    "private_guardrail",
}
_GATES = {
    "runtime_wiring_allowed": False,
    "skill_update_allowed": False,
    "visible_behavior_change_allowed": False,
}
_DETERMINISTIC_ROLE = [
    "compute_compiled_card_deck_key",
    "lookup_cached_deck_only",
    "derive_step6_ledger_signal",
    "derive_answer_delta_specificity",
    "validate_payload_gate",
    "derive_shadow_visibility_decision",
    "archive_only_no_visible_output",
]
_CONCRETE_ANSWER_DELTA_FIELDS = (
    "added_entities",
    "removed_entities",
    "reordered_sequences",
)
_STRUCTURAL_ANSWER_DELTA_FIELD = "structural_delta"
_UNLOCKING_ANSWER_DELTA_SPECIFICITY = {
    "concrete_delta_present",
    "structural_delta_present",
}
_STRUCTURAL_DELTA_MARKERS = (
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
_VAGUE_STRUCTURAL_DELTA_PHRASES = (
    "better framing",
    "clearer framing",
    "sharper framing",
    "structural framing",
    "structural change",
)


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _v60_selected_chunk_ids(result_payload: dict[str, Any]) -> list[str]:
    v60 = _as_mapping(result_payload.get("v60_enrichment"))
    telemetry = _as_mapping(v60.get("telemetry"))
    ids = [
        str(item)
        for item in _as_list(telemetry.get("selected_chunk_ids"))
        if str(item).strip()
    ]
    return sorted(set(ids))


def _key_material(result_payload: dict[str, Any]) -> dict[str, Any]:
    extraction = _as_mapping(result_payload.get("extraction"))
    return {
        "schema_version": SCHEMA_VERSION,
        "card_deck_schema_version": CARD_DECK_SCHEMA_VERSION,
        "decision_situation": str(extraction.get("decision_situation") or ""),
        "original_framing": str(extraction.get("original_framing") or ""),
        "prompt_versions": _as_mapping(result_payload.get("prompt_versions")),
        "v60_selected_chunk_ids": _v60_selected_chunk_ids(result_payload),
    }


def _compiled_card_deck_key(key_material: dict[str, Any]) -> str:
    digest = hashlib.sha256(_canonical_json(key_material).encode("utf-8")).hexdigest()
    return f"pre-step6-shadow-card-deck-{digest[:16]}"


def _deck_cache_path(cache_dir: Path | None, compiled_key: str) -> Path | None:
    if cache_dir is None:
        return None
    return Path(cache_dir) / f"{compiled_key}{_CACHE_FILE_SUFFIX}"


def _resolve_operator_cache_ref(cache_dir: Path | None, cache_ref: Path | str | None) -> Path | None:
    if cache_ref is None:
        return None
    raw = str(cache_ref).strip()
    if not raw:
        return None
    candidate = Path(raw).expanduser()
    if candidate.exists() or candidate.is_absolute():
        return candidate
    if cache_dir is None:
        return candidate
    cache_dir_path = Path(cache_dir)
    cache_candidate = cache_dir_path / raw
    if cache_candidate.exists() or raw.endswith(_CACHE_FILE_SUFFIX):
        return cache_candidate
    return cache_dir_path / f"{raw}{_CACHE_FILE_SUFFIX}"


def _read_cached_deck(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        deck = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if not isinstance(deck, dict) or deck.get("schema_version") != CARD_DECK_SCHEMA_VERSION:
        return None, "invalid_card_deck_schema"
    return deck, ""


def _load_cached_deck(
    cache_dir: Path | None,
    compiled_key: str,
    *,
    cache_ref: Path | str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    exact_cache_path = _deck_cache_path(cache_dir, compiled_key)
    operator_cache_path = _resolve_operator_cache_ref(cache_dir, cache_ref)
    base = {
        "cache_dir": str(cache_dir) if cache_dir is not None else "",
        "exact_cache_ref": str(exact_cache_path) if exact_cache_path is not None else "",
        "operator_cache_ref": str(operator_cache_path) if operator_cache_path is not None else "",
        "live_card_generation_allowed": False,
    }

    if exact_cache_path is not None and exact_cache_path.exists():
        deck, error = _read_cached_deck(exact_cache_path)
        if not error and deck is not None:
            return (
                {
                    **base,
                    "state": "cache_hit",
                    "resolution": "exact_key",
                    "cache_ref": str(exact_cache_path),
                    "card_count": len(_as_list(deck.get("cards"))),
                },
                deck,
            )
        return (
            {
                **base,
                "state": "cache_invalid",
                "resolution": "exact_key",
                "cache_ref": str(exact_cache_path),
                "miss_behavior": "stand_down_to_current_step6",
                "error": error,
            },
            {},
        )

    if operator_cache_path is not None:
        if not operator_cache_path.exists():
            return (
                {
                    **base,
                    "state": "cache_miss",
                    "resolution": "operator_cache_ref",
                    "cache_ref": str(operator_cache_path),
                    "miss_behavior": "stand_down_to_current_step6",
                    "error": "operator_cache_ref_missing",
                },
                {},
            )
        deck, error = _read_cached_deck(operator_cache_path)
        if not error and deck is not None:
            return (
                {
                    **base,
                    "state": "cache_hit",
                    "resolution": "operator_cache_ref",
                    "cache_ref": str(operator_cache_path),
                    "card_count": len(_as_list(deck.get("cards"))),
                },
                deck,
            )
        return (
            {
                **base,
                "state": "cache_invalid",
                "resolution": "operator_cache_ref",
                "cache_ref": str(operator_cache_path),
                "miss_behavior": "stand_down_to_current_step6",
                "error": error,
            },
            {},
        )

    return (
        {
            **base,
            "state": "cache_miss",
            "resolution": "exact_key",
            "cache_ref": "",
            "miss_behavior": "stand_down_to_current_step6",
        },
        {},
    )


def derive_step6_ledger_signal(step6_ledger: dict[str, Any] | None) -> str:
    """Reduce Step 6's own private ledger to a visibility-policy input.

    This is not a wisdom judgment. The only positive signal is Step 6 saying,
    in its private ledger, that non-anchor card pressure created additive
    pressure and was used/combined. Everything else is conservative.
    """
    ledger = _as_mapping(step6_ledger)
    items = _as_list(ledger.get("items"))
    if not items:
        return "missing_or_unclear"

    non_anchor_items: list[dict[str, Any]] = []
    for raw_item in items:
        item = _as_mapping(raw_item)
        source_id = str(item.get("source_id") or "")
        if source_id in _ANCHOR_SOURCE_IDS:
            continue
        non_anchor_items.append(item)

    if not non_anchor_items:
        return "missing_or_unclear"

    for item in non_anchor_items:
        disposition = str(item.get("disposition") or "")
        novelty_role = str(item.get("novelty_role") or "")
        if novelty_role == "additive_pressure" and disposition in {"used", "combined"}:
            return "additive_pressure_present"

    if all(
        str(item.get("disposition") or "") in _PRIVATE_OR_CONFIRMING_DISPOSITIONS
        or str(item.get("novelty_role") or "") in _PRIVATE_OR_CONFIRMING_ROLES
        for item in non_anchor_items
    ):
        return "all_private_or_confirming"

    return "missing_or_unclear"


def derive_answer_delta_specificity(step6_ledger: dict[str, Any] | None) -> str:
    """Mechanically classify whether additive ledger items name concrete deltas."""
    additive_items = _additive_non_anchor_items(step6_ledger)
    if not additive_items:
        return "not_applicable"

    saw_reframe = False
    saw_structural_delta = False
    saw_delta = False
    for item in additive_items:
        delta = _as_mapping(item.get("answer_delta"))
        if any(_non_empty_string_list(delta.get(field)) for field in _CONCRETE_ANSWER_DELTA_FIELDS):
            saw_delta = True
        if _specific_structural_delta_present(delta.get(_STRUCTURAL_ANSWER_DELTA_FIELD)):
            saw_structural_delta = True
        if _non_empty_string_list(delta.get("reframed_emphasis")):
            saw_reframe = True

    if saw_delta:
        return "concrete_delta_present"
    if saw_structural_delta:
        return "structural_delta_present"
    if saw_reframe:
        return "reframe_only"
    return "missing_or_unclear"


def _additive_non_anchor_items(step6_ledger: dict[str, Any] | None) -> list[dict[str, Any]]:
    ledger = _as_mapping(step6_ledger)
    items = _as_list(ledger.get("items"))
    additive_items: list[dict[str, Any]] = []
    for raw_item in items:
        item = _as_mapping(raw_item)
        source_id = str(item.get("source_id") or "")
        if source_id in _ANCHOR_SOURCE_IDS:
            continue
        disposition = str(item.get("disposition") or "")
        novelty_role = str(item.get("novelty_role") or "")
        if novelty_role == "additive_pressure" and disposition in {"used", "combined"}:
            additive_items.append(item)
    return additive_items


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)


def _specific_structural_delta_present(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    return any(_is_specific_structural_delta(item) for item in value)


def _is_specific_structural_delta(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = " ".join(value.lower().split())
    if not text:
        return False
    words = [word.strip(".,:;()[]{}!?") for word in text.split()]
    marker_present = any(marker in text for marker in _STRUCTURAL_DELTA_MARKERS)
    if len(words) < 5 or not marker_present:
        return False
    return not any(text == phrase or text.endswith(f" {phrase}") for phrase in _VAGUE_STRUCTURAL_DELTA_PHRASES)


def _decision(
    *,
    result: str,
    why: str,
    cognitive_signal_source: str,
) -> dict[str, Any]:
    return {
        "result": result,
        "why": why,
        "cognitive_signal_source": cognitive_signal_source,
        "normal_runtime_reviewer_calls": 0,
        "applied_to_user_visible_output": False,
    }


def build_pre_step6_shadow_portfolio(
    *,
    result_payload: dict[str, Any],
    mode: str = "off",
    cache_dir: Path | str | None = None,
    cache_ref: Path | str | None = None,
    step6_ledger: dict[str, Any] | None = None,
    payload_gate: dict[str, Any] | None = None,
    custody_valid: bool = True,
) -> dict[str, Any]:
    """Build the dormant shadow portfolio artifact.

    ``mode="shadow"`` records what the proposed policy would do. ``mode="off"``
    records only that no shadow evaluation ran. Neither mode mutates Step 6
    output.
    """
    normalized_mode = str(mode or "off").lower()
    cache_dir_path = Path(cache_dir) if cache_dir is not None else None
    material = _key_material(_as_mapping(result_payload))
    compiled_key = _compiled_card_deck_key(material)
    payload_gate_payload = _as_mapping(payload_gate) or {"status": "not_supplied"}
    payload_gate_status = str(
        payload_gate_payload.get("status")
        or payload_gate_payload.get("gate_result")
        or "missing_or_unclear"
    )
    custody_validation = {
        "status": "valid" if custody_valid else "invalid",
        "valid": bool(custody_valid),
    }

    if normalized_mode != "shadow":
        payload = {
            "schema_version": SCHEMA_VERSION,
            "runtime_policy": "dormant_shadow_only",
            "status": "disabled",
            "mode": normalized_mode,
            "promotion_effect": "none_shadow_only",
            "key_material": material,
            "compiled_card_deck_key": compiled_key,
            "cache": {
                "state": "not_checked",
                "cache_dir": str(cache_dir_path) if cache_dir_path is not None else "",
                "cache_ref": "",
                "live_card_generation_allowed": False,
            },
            "step6_ledger_signal": "not_run",
            "answer_delta_specificity": "not_run",
            "step6_private_ledger": step6_ledger or {"status": "not_supplied"},
            "payload_gate": payload_gate_payload,
            "custody_validation": custody_validation,
            "shadow_visibility_decision": _decision(
                result="current_step6_visible_shadow_disabled",
                why="Pre-Step-6 shadow portfolio mode is disabled.",
                cognitive_signal_source="not_run",
            ),
            "deterministic_role": list(_DETERMINISTIC_ROLE),
            "gates": dict(_GATES),
            "cost_envelope": {
                "normal_runtime_reviewer_calls": 0,
                "live_card_generation_allowed": False,
                "net_new_llm_calls": 0,
            },
        }
        validate_pre_step6_shadow_portfolio(payload)
        return payload

    cache_payload, deck = _load_cached_deck(
        cache_dir_path,
        compiled_key,
        cache_ref=cache_ref,
    )
    ledger_signal = derive_step6_ledger_signal(step6_ledger)
    answer_delta_specificity = derive_answer_delta_specificity(step6_ledger)

    if cache_payload.get("state") != "cache_hit":
        status = "shadow_cache_miss"
        decision = _decision(
            result="current_step6_visible_no_deck",
            why="Cached card deck is unavailable; shadow mode records stand-down only.",
            cognitive_signal_source="not_run",
        )
    elif not custody_valid:
        status = "shadow_resolved"
        decision = _decision(
            result="current_step6_visible_custody_guardrail_shadow_only",
            why="Cached card deck exists, but custody validation failed.",
            cognitive_signal_source="deterministic_guardrail",
        )
    elif payload_gate_status == "introduced_omission":
        status = "shadow_resolved"
        decision = _decision(
            result="anchor_visible_payload_omission_guardrail_shadow_only",
            why="Payload omission gate detected a protected anchor omission.",
            cognitive_signal_source="deterministic_guardrail",
        )
    elif (
        ledger_signal == "additive_pressure_present"
        and answer_delta_specificity not in _UNLOCKING_ANSWER_DELTA_SPECIFICITY
    ):
        status = "shadow_resolved"
        decision = _decision(
            result="anchor_visible_answer_delta_guardrail_shadow_only",
            why=(
                "Step 6 recorded additive pressure, but did not record a specific "
                "concrete or structural answer delta beyond abstract reframing."
            ),
            cognitive_signal_source="deterministic_guardrail",
        )
    elif ledger_signal == "additive_pressure_present":
        status = "shadow_resolved"
        decision = _decision(
            result="deck_visible_shadow_only",
            why="Step 6 recorded additive pressure and deterministic guards passed.",
            cognitive_signal_source="step6_private_ledger",
        )
    elif ledger_signal == "all_private_or_confirming":
        status = "shadow_resolved"
        decision = _decision(
            result="anchor_visible_deck_private_shadow_only",
            why="Step 6 kept non-anchor pressure private or confirming.",
            cognitive_signal_source="step6_private_ledger",
        )
    else:
        status = "shadow_resolved"
        decision = _decision(
            result="anchor_visible_unclear_ledger_guardrail_shadow_only",
            why="Step 6 ledger is missing or unclear; shadow mode cannot infer cognition.",
            cognitive_signal_source="missing_or_unclear",
        )

    payload = {
        "schema_version": SCHEMA_VERSION,
        "runtime_policy": "dormant_shadow_only",
        "status": status,
        "mode": normalized_mode,
        "promotion_effect": "none_shadow_only",
        "key_material": material,
        "compiled_card_deck_key": compiled_key,
        "cache": cache_payload,
        "cached_card_deck_summary": {
            "schema_version": deck.get("schema_version", ""),
            "card_count": len(_as_list(deck.get("cards"))),
        } if deck else {},
        "step6_ledger_signal": ledger_signal,
        "answer_delta_specificity": answer_delta_specificity,
        "step6_private_ledger": step6_ledger or {"status": "not_supplied"},
        "payload_gate": payload_gate_payload,
        "custody_validation": custody_validation,
        "shadow_visibility_decision": decision,
        "deterministic_role": list(_DETERMINISTIC_ROLE),
        "gates": dict(_GATES),
        "cost_envelope": {
            "normal_runtime_reviewer_calls": 0,
            "live_card_generation_allowed": False,
            "net_new_llm_calls": 0,
        },
    }
    validate_pre_step6_shadow_portfolio(payload)
    return payload


def validate_pre_step6_shadow_portfolio(payload: dict[str, Any]) -> None:
    """Validate the safety envelope for the dormant artifact."""
    if not isinstance(payload, dict):
        raise ValueError("pre-Step-6 shadow portfolio payload must be an object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("invalid pre-Step-6 shadow portfolio schema_version")
    decision = _as_mapping(payload.get("shadow_visibility_decision"))
    if decision.get("applied_to_user_visible_output") is not False:
        raise ValueError("shadow portfolio must not apply to user-visible output")
    if int(decision.get("normal_runtime_reviewer_calls") or 0) != 0:
        raise ValueError("shadow portfolio must not require runtime reviewer calls")
    cache = _as_mapping(payload.get("cache"))
    if cache.get("live_card_generation_allowed") is not False:
        raise ValueError("shadow portfolio must not generate live card decks")
    if payload.get("promotion_effect") != "none_shadow_only":
        raise ValueError("shadow portfolio must not promote runtime behavior")
    if payload.get("gates") != _GATES:
        raise ValueError("shadow portfolio gates must remain closed")


def write_pre_step6_shadow_portfolio_sidecar(
    payload: dict[str, Any],
    *,
    tmp_dir: Path | str = "/tmp",
    run_id: str,
) -> Path:
    validate_pre_step6_shadow_portfolio(payload)
    path = Path(tmp_dir) / f"lolla_{run_id}_pre_step6_shadow_portfolio.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
