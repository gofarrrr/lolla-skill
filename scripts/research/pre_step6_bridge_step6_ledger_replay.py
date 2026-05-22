#!/usr/bin/env python3
"""Research-only Step 6 ledger replay for false-standdown bridge cases.

This slice tests whether Step 6 itself can supply the additive-pressure signal
that the visibility redesign relies on. It uses the pre-registered bridge cases
as private context and keeps runtime dormant.
"""
from __future__ import annotations

import json
import argparse
import dataclasses
import os
from pathlib import Path
import sys
from typing import Iterable, Sequence

from pre_step6_false_standdown_bridge_probe import validate_bridge_probe_contract
from pre_step6_raw_artifacts import validate_public_answer_hygiene


SCHEMA_VERSION = "pre_step6_bridge_step6_ledger_replay.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "bridge_step6_ledger_replay_v0"
REPLAY_MODE = "bridge_packet_step6_ledger_replay"
RESULT_SCHEMA_VERSION = "pre_step6_bridge_step6_ledger_replay_result.v1"
DEFAULT_OUT_DIR = Path("research/pre-step6-bridge-step6-ledger-replays")
DEFAULT_CONTRACT_REF = (
    "research/pre-step6-false-standdown-bridge-probe/"
    "false-standdown-bridge-probe.v1.json"
)
ALLOWED_SOURCE_IDS = ("anchor_visible_candidate", "deck_pressure_candidate")
ALLOWED_DISPOSITIONS = frozenset(
    {"used", "combined", "rejected", "deferred", "private_guardrail"}
)
ALLOWED_NOVELTY_ROLES = frozenset(
    {"visible_backbone", "additive_pressure", "confirming_support", "private_guardrail"}
)
ALLOWED_LEDGER_SIGNALS = frozenset(
    {"additive_pressure_present", "all_private_or_confirming", "missing_or_unclear"}
)
DETERMINISTIC_ROLE = (
    "validate_bridge_contract_case",
    "validate_step6_ledger_schema",
    "derive_ledger_signal",
    "derive_answer_delta_specificity",
    "preserve_audit_custody",
)
LEGACY_DETERMINISTIC_ROLE = (
    "validate_bridge_contract_case",
    "validate_step6_ledger_schema",
    "derive_ledger_signal",
    "preserve_audit_custody",
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "case_id",
        "replay_mode",
        "source_bridge_probe_contract",
        "input_packet",
        "provider_metadata",
        "step6_output",
        "ledger_signal",
        "answer_delta_specificity",
        "visibility_redesign_read",
        "deterministic_role",
        "gates",
        "notes",
    }
)
RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "case_results",
        "replay_result",
        "answer_delta_replay_result",
        "gates",
        "notes",
    }
)
CASE_RESULT_FIELDS = frozenset(
    {
        "case_id",
        "ledger_signal",
        "answer_delta_specificity",
        "would_unlock_redesigned_policy",
        "would_unlock_answer_delta_guarded_policy",
    }
)
OPTIONAL_TOP_LEVEL_FIELDS = frozenset({"notes", "answer_delta_specificity"})
OPTIONAL_RESULT_FIELDS = frozenset({"notes", "answer_delta_replay_result"})
OPTIONAL_CASE_RESULT_FIELDS = frozenset(
    {"answer_delta_specificity", "would_unlock_answer_delta_guarded_policy"}
)
INPUT_PACKET_FIELDS = frozenset(
    {
        "case_brief",
        "pre_run_failure_hypothesis",
        "expected_deck_adds",
        "anchor_risk_if_hidden",
        "anchor_visible_candidate",
        "deck_pressure_candidate",
    }
)
PROVIDER_METADATA_FIELDS = frozenset(
    {
        "provider",
        "provider_name",
        "model",
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
STEP6_OUTPUT_FIELDS = frozenset({"answer_core", "private_bridge_consideration_ledger"})
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
UNLOCKING_ANSWER_DELTA_SPECIFICITY = frozenset(
    {"concrete_delta_present", "structural_delta_present"}
)
ALLOWED_ANSWER_DELTA_SPECIFICITY = frozenset(
    {
        "concrete_delta_present",
        "structural_delta_present",
        "reframe_only",
        "missing_or_unclear",
        "not_applicable",
    }
)
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
VISIBILITY_READ_FIELDS = frozenset(
    {
        "would_unlock_redesigned_policy",
        "would_unlock_answer_delta_guarded_policy",
        "policy_dependency",
        "answer_delta_dependency",
    }
)
VISIBILITY_READ_REQUIRED_FIELDS = frozenset(
    {"would_unlock_redesigned_policy", "policy_dependency"}
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
PRIVATE_LABEL_TERMS = (
    "anchor_visible_candidate",
    "deck_pressure_candidate",
    "private_bridge_consideration_ledger",
    "ledger",
    "card deck",
    "private label",
)


class BridgeStep6LedgerReplayValidationError(ValueError):
    pass


def build_static_bridge_step6_replay(
    *,
    contract: dict[str, object],
    case_id: str,
    deck_novelty_role: str,
    deck_disposition: str,
) -> dict[str, object]:
    validate_bridge_probe_contract(contract)
    case = _case_by_id(contract, case_id)
    candidates = _answer_candidates(case, case_id)
    answer_core = (
        _string(candidates["deck_visible"])
        if deck_novelty_role == "additive_pressure"
        and deck_disposition in {"used", "combined"}
        else _string(candidates["anchor_visible"])
    )
    step6_output = {
        "answer_core": answer_core,
        "private_bridge_consideration_ledger": [
            {
                "source_id": "anchor_visible_candidate",
                "disposition": "used",
                "novelty_role": "visible_backbone",
                "why": "The anchor supplied the stable public backbone.",
                "visible_effect": "Kept the answer grounded in the original answer shape.",
                "answer_delta": _empty_answer_delta(),
            },
            {
                "source_id": "deck_pressure_candidate",
                "disposition": deck_disposition,
                "novelty_role": deck_novelty_role,
                "why": "Static replay fixture for Step 6 deck-pressure consideration.",
                "visible_effect": (
                    "Added concrete bridge pressure."
                    if deck_novelty_role == "additive_pressure"
                    and deck_disposition in {"used", "combined"}
                    else "none"
                ),
                "answer_delta": (
                    {
                        "added_entities": list(case.get("expected_deck_adds", [])),
                        "removed_entities": [],
                        "reordered_sequences": [],
                        "structural_delta": [],
                        "reframed_emphasis": [],
                    }
                    if deck_novelty_role == "additive_pressure"
                    and deck_disposition in {"used", "combined"}
                    else _empty_answer_delta()
                ),
            },
        ],
    }
    ledger_signal = derive_ledger_signal(step6_output)
    answer_delta_specificity = derive_answer_delta_specificity(step6_output)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case_id,
        "replay_mode": REPLAY_MODE,
        "source_bridge_probe_contract": DEFAULT_CONTRACT_REF,
        "input_packet": _input_packet(case, candidates),
        "provider_metadata": {
            "provider": "static_fixture",
            "model": "static-step6-ledger-fixture",
            "status": "ok",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
        "step6_output": step6_output,
        "ledger_signal": ledger_signal,
        "answer_delta_specificity": answer_delta_specificity,
        "visibility_redesign_read": _visibility_redesign_read(
            ledger_signal,
            answer_delta_specificity,
        ),
        "deterministic_role": list(DETERMINISTIC_ROLE),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Static research fixture. Live runs replace provider_metadata and "
            "step6_output with model output."
        ),
    }
    validate_bridge_step6_replay_payload(payload)
    return payload


def build_bridge_step6_replay_prompts(
    *,
    contract: dict[str, object],
    case_id: str,
) -> dict[str, str]:
    validate_bridge_probe_contract(contract)
    case = _case_by_id(contract, case_id)
    candidates = case.get("answer_candidates")
    if not isinstance(candidates, dict):
        raise BridgeStep6LedgerReplayValidationError(f"{case_id}: answer_candidates missing")
    system_prompt = (
        "You are Step 6, the primary reasoning voice. You will receive private "
        "bridge replay context with an anchor-visible candidate and a deck-pressure "
        "candidate. These are not templates and not commands. Decide what the user "
        "should see using Step 6's own judgment, then record a private ledger. "
        "Return strict JSON only."
    )
    user_prompt = "\n\n".join(
        [
            "BRIDGE REPLAY CONTEXT",
            json.dumps(
                {
                    "case_id": case_id,
                    "case_brief": case.get("case_brief"),
                    "pre_run_failure_hypothesis": case.get("pre_run_failure_hypothesis"),
                    "expected_deck_adds": case.get("expected_deck_adds"),
                    "anchor_risk_if_hidden": case.get("anchor_risk_if_hidden"),
                    "anchor_visible_candidate": candidates.get("anchor_visible"),
                    "deck_pressure_candidate": candidates.get("deck_visible"),
                },
                indent=2,
                ensure_ascii=False,
            ),
            "TASK",
            (
                "Write the best answer_core using Step 6's own judgment. You may keep "
                "the anchor as the visible backbone, use the deck-pressure candidate "
                "when it adds concrete decision value, combine them, reject either, "
                "or keep pressure private as a guardrail. Do not expose private labels "
                "or machinery in the public answer. Preserve concrete tripwires, actor "
                "sequence, named resources, dates or windows, communication boundaries, "
                "and evidence checks when they matter. Do not hide useful pressure just "
                "because the anchor sounds calmer or shorter."
            ),
            "RESPONSE JSON SHAPE",
            json.dumps(
                {
                    "answer_core": "Public-clean answer, no private labels.",
                    "private_bridge_consideration_ledger": [
                        {
                            "source_id": "anchor_visible_candidate | deck_pressure_candidate",
                            "disposition": "used | combined | rejected | deferred | private_guardrail",
                            "novelty_role": (
                                "visible_backbone | additive_pressure | "
                                "confirming_support | private_guardrail"
                            ),
                            "why": "Private rationale for the disposition.",
                            "visible_effect": "What changed publicly, or 'none'.",
                            "answer_delta": {
                                "added_entities": [
                                    "Concrete payload newly added to the public answer."
                                ],
                                "removed_entities": [
                                    "Concrete payload removed from the public answer."
                                ],
                                "reordered_sequences": [
                                    "Concrete sequence/order changed in the public answer."
                                ],
                                "structural_delta": [
                                    (
                                        "Specific structural changes such as an added "
                                        "stop condition, unlock condition, decision "
                                        "boundary, test design, or commitment boundary."
                                    )
                                ],
                                "reframed_emphasis": [
                                    "Abstract framing, emphasis, tone, or interpretation shift."
                                ],
                            },
                        }
                    ],
                },
                indent=2,
            ),
            (
                "ANSWER_DELTA RULE: If you mark deck_pressure_candidate as "
                "additive_pressure with disposition used or combined, populate "
                "added_entities, removed_entities, or reordered_sequences when the "
                "visible answer changed in a concrete entity/order way. Populate "
                "structural_delta only when the public answer gains a specific "
                "structural element, such as a named stop condition, unlock "
                "condition, decision boundary, test design, or commitment boundary. "
                "Do not use vague entries like 'added structural framing'. Use "
                "reframed_emphasis only for abstract framing/tone/emphasis changes. "
                "If there is no concrete or specific structural visible-answer "
                "delta, do not overstate the deck as publicly additive."
            ),
        ]
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}


def load_bridge_step6_replay_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BridgeStep6LedgerReplayValidationError(f"{path}: payload must be an object")
    return payload


def write_bridge_step6_replay(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_bridge_step6_replay_payload(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{_string(payload['case_id'])}.bridge-step6-ledger-replay.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_bridge_step6_replay_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_bridge_step6_replay_errors(payload, path=Path(path)))
    if errors:
        raise BridgeStep6LedgerReplayValidationError("; ".join(errors))


def iter_bridge_step6_replay_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(TOP_LEVEL_FIELDS - OPTIONAL_TOP_LEVEL_FIELDS)
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {SCHEMA_VERSION}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    if payload.get("replay_mode") != REPLAY_MODE:
        yield f"{path / 'replay_mode'}: must be {REPLAY_MODE}"
    if not _string(payload.get("source_bridge_probe_contract")).strip():
        yield f"{path / 'source_bridge_probe_contract'}: must be non-empty"
    yield from _validate_input_packet(payload.get("input_packet"), path / "input_packet")
    yield from _validate_provider_metadata(
        payload.get("provider_metadata"),
        path / "provider_metadata",
    )
    step6_output = payload.get("step6_output")
    yield from _validate_step6_output(step6_output, path / "step6_output")
    expected_signal = (
        derive_ledger_signal(step6_output)
        if isinstance(step6_output, dict)
        else "missing_or_unclear"
    )
    if payload.get("ledger_signal") != expected_signal:
        yield f"{path / 'ledger_signal'}: must be derived from Step 6 ledger"
    expected_specificity = (
        derive_answer_delta_specificity(step6_output)
        if isinstance(step6_output, dict)
        else "missing_or_unclear"
    )
    if "answer_delta_specificity" in payload and payload.get(
        "answer_delta_specificity"
    ) != expected_specificity:
        yield f"{path / 'answer_delta_specificity'}: must be derived from Step 6 ledger"
    yield from _validate_visibility_read(
        payload.get("visibility_redesign_read"),
        path / "visibility_redesign_read",
        ledger_signal=_string(payload.get("ledger_signal")),
        answer_delta_specificity=expected_specificity,
    )
    allowed_roles = [list(DETERMINISTIC_ROLE)]
    if "answer_delta_specificity" not in payload:
        allowed_roles.append(list(LEGACY_DETERMINISTIC_ROLE))
    if payload.get("deterministic_role") not in allowed_roles:
        yield f"{path / 'deterministic_role'}: invalid deterministic role"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def build_bridge_step6_replay_result(
    *,
    replays: Sequence[dict[str, object]],
) -> dict[str, object]:
    for replay in replays:
        validate_bridge_step6_replay_payload(replay)
    case_results = [
        {
            "case_id": _string(replay.get("case_id")),
            "ledger_signal": _string(replay.get("ledger_signal")),
            "answer_delta_specificity": _answer_delta_specificity_for_replay(replay),
            "would_unlock_redesigned_policy": bool(
                isinstance(replay.get("visibility_redesign_read"), dict)
                and replay["visibility_redesign_read"].get("would_unlock_redesigned_policy")
                is True
            ),
            "would_unlock_answer_delta_guarded_policy": bool(
                isinstance(replay.get("visibility_redesign_read"), dict)
                and replay["visibility_redesign_read"].get(
                    "would_unlock_answer_delta_guarded_policy"
                )
                is True
            ),
        }
        for replay in sorted(replays, key=lambda item: _string(item.get("case_id")))
    ]
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "case_results": case_results,
        "replay_result": _aggregate_replay_result(case_results),
        "answer_delta_replay_result": _aggregate_answer_delta_replay_result(case_results),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Aggregate for bridge Step 6 ledger replay. This is upstream evidence "
            "for the visibility-policy redesign, not runtime promotion."
        ),
    }
    validate_bridge_step6_replay_result(payload)
    return payload


def load_bridge_step6_replay_result(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BridgeStep6LedgerReplayValidationError(f"{path}: payload must be an object")
    return payload


def write_bridge_step6_replay_result(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_bridge_step6_replay_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "bridge-step6-ledger-replay-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_bridge_step6_replay_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_bridge_step6_replay_result_errors(payload, path=Path(path)))
    if errors:
        raise BridgeStep6LedgerReplayValidationError("; ".join(errors))


def iter_bridge_step6_replay_result_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(RESULT_FIELDS - OPTIONAL_RESULT_FIELDS)
    yield from _unknown_fields(payload, RESULT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != RESULT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {RESULT_SCHEMA_VERSION}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if payload.get("promotion_effect") != "none_research_only":
        yield f"{path / 'promotion_effect'}: must be none_research_only"
    results = payload.get("case_results")
    if not isinstance(results, list):
        yield f"{path / 'case_results'}: must be a list"
    else:
        for index, result in enumerate(results):
            yield from _validate_case_result(result, path / "case_results" / str(index))
        expected = _aggregate_replay_result(results)
        if payload.get("replay_result") != expected:
            yield f"{path / 'replay_result'}: must be {expected}"
        if "answer_delta_replay_result" in payload:
            expected_delta_result = _aggregate_answer_delta_replay_result(results)
            if payload.get("answer_delta_replay_result") != expected_delta_result:
                yield (
                    f"{path / 'answer_delta_replay_result'}: "
                    f"must be {expected_delta_result}"
                )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def write_fixture_suite(*, contract: dict[str, object], out_dir: Path) -> list[Path]:
    validate_bridge_probe_contract(contract)
    paths: list[Path] = []
    replays = []
    for case in contract["probe_cases"]:
        assert isinstance(case, dict)
        payload = build_static_bridge_step6_replay(
            contract=contract,
            case_id=_string(case["case_id"]),
            deck_novelty_role="additive_pressure",
            deck_disposition="used",
        )
        replays.append(payload)
        paths.append(write_bridge_step6_replay(payload=payload, out_dir=out_dir))
    result = build_bridge_step6_replay_result(replays=replays)
    paths.append(write_bridge_step6_replay_result(payload=result, out_dir=out_dir))
    return paths


def run_live_replay(
    *,
    contract: dict[str, object],
    case_id: str,
    provider: str,
    model: str,
    env_file: Path | None,
    out_dir: Path,
    dry_run: bool,
) -> Path | None:
    validate_bridge_probe_contract(contract)
    if env_file is not None:
        _load_env_file(env_file)
    if model:
        os.environ["LOLLA_OPENROUTER_MODEL"] = model
    prompts = build_bridge_step6_replay_prompts(contract=contract, case_id=case_id)
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
        stage="pre_step6_bridge_step6_ledger_replay",
        tendency_id=case_id,
    )
    provider_metadata = _provider_metadata_dict(metadata)
    if _string(provider_metadata.get("status")) != "ok":
        raise BridgeStep6LedgerReplayValidationError(
            "live bridge Step 6 ledger replay failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    case = _case_by_id(contract, case_id)
    candidates = _answer_candidates(case, case_id)
    step6_output = normalize_bridge_step6_output(output)
    ledger_signal = derive_ledger_signal(step6_output)
    answer_delta_specificity = derive_answer_delta_specificity(step6_output)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case_id,
        "replay_mode": REPLAY_MODE,
        "source_bridge_probe_contract": DEFAULT_CONTRACT_REF,
        "input_packet": _input_packet(case, candidates),
        "provider_metadata": provider_metadata,
        "step6_output": step6_output,
        "ledger_signal": ledger_signal,
        "answer_delta_specificity": answer_delta_specificity,
        "visibility_redesign_read": _visibility_redesign_read(
            ledger_signal,
            answer_delta_specificity,
        ),
        "deterministic_role": list(DETERMINISTIC_ROLE),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Live research-only bridge Step 6 replay. The model wrote the answer "
            "and private ledger; code only normalized and derived the ledger signal."
        ),
    }
    return write_bridge_step6_replay(payload=payload, out_dir=out_dir)


def derive_ledger_signal(step6_output: object) -> str:
    if not isinstance(step6_output, dict):
        return "missing_or_unclear"
    ledger = step6_output.get("private_bridge_consideration_ledger")
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
    ledger = step6_output.get("private_bridge_consideration_ledger")
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
            return "missing_or_unclear"
        if any(_non_empty_string_list(delta.get(field)) for field in CONCRETE_ANSWER_DELTA_FIELDS):
            return "concrete_delta_present"
        if _specific_structural_delta_present(delta.get(STRUCTURAL_ANSWER_DELTA_FIELD)):
            return "structural_delta_present"
        if _non_empty_string_list(delta.get("reframed_emphasis")):
            saw_reframe = True
    return "reframe_only" if saw_reframe else "missing_or_unclear"


def normalize_bridge_step6_output(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    ledger = value.get("private_bridge_consideration_ledger")
    if not isinstance(ledger, list):
        ledger = []
    by_source = {
        _string(item.get("source_id")): item
        for item in ledger
        if isinstance(item, dict)
    }
    normalized_ledger = []
    for source_id in ALLOWED_SOURCE_IDS:
        item = by_source.get(source_id, {})
        normalized_ledger.append(
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
        "private_bridge_consideration_ledger": normalized_ledger,
    }


def _aggregate_replay_result(case_results: Sequence[object]) -> str:
    additive = [
        isinstance(result, dict)
        and result.get("ledger_signal") == "additive_pressure_present"
        and result.get("would_unlock_redesigned_policy") is True
        for result in case_results
    ]
    if additive and all(additive):
        return "step6_additive_signal_supported"
    if any(additive):
        return "step6_additive_signal_mixed"
    return "step6_additive_signal_not_supported"


def _aggregate_answer_delta_replay_result(case_results: Sequence[object]) -> str:
    guarded = [
        isinstance(result, dict)
        and result.get("ledger_signal") == "additive_pressure_present"
        and result.get("answer_delta_specificity") in UNLOCKING_ANSWER_DELTA_SPECIFICITY
        and result.get("would_unlock_answer_delta_guarded_policy") is True
        for result in case_results
    ]
    if guarded and all(guarded):
        return "answer_delta_bridge_support_preserved"
    if any(guarded):
        return "answer_delta_bridge_support_mixed"
    return "answer_delta_bridge_support_not_supported"


def _answer_delta_specificity_for_replay(replay: dict[str, object]) -> str:
    existing = _string(replay.get("answer_delta_specificity"))
    if existing in ALLOWED_ANSWER_DELTA_SPECIFICITY:
        return existing
    return derive_answer_delta_specificity(replay.get("step6_output"))


def _case_by_id(contract: dict[str, object], case_id: str) -> dict[str, object]:
    cases = contract.get("probe_cases")
    if not isinstance(cases, list):
        raise BridgeStep6LedgerReplayValidationError("probe_cases missing")
    for case in cases:
        if isinstance(case, dict) and case.get("case_id") == case_id:
            return case
    raise BridgeStep6LedgerReplayValidationError(f"unknown bridge case: {case_id}")


def _answer_candidates(case: dict[str, object], case_id: str) -> dict[str, object]:
    candidates = case.get("answer_candidates")
    if not isinstance(candidates, dict):
        raise BridgeStep6LedgerReplayValidationError(f"{case_id}: answer_candidates missing")
    for arm in ("anchor_visible", "deck_visible"):
        if not _string(candidates.get(arm)).strip():
            raise BridgeStep6LedgerReplayValidationError(f"{case_id}: {arm} missing")
    return candidates


def _input_packet(
    case: dict[str, object],
    candidates: dict[str, object],
) -> dict[str, object]:
    return {
        "case_brief": case.get("case_brief"),
        "pre_run_failure_hypothesis": case.get("pre_run_failure_hypothesis"),
        "expected_deck_adds": case.get("expected_deck_adds"),
        "anchor_risk_if_hidden": case.get("anchor_risk_if_hidden"),
        "anchor_visible_candidate": candidates.get("anchor_visible"),
        "deck_pressure_candidate": candidates.get("deck_visible"),
    }


def _visibility_redesign_read(
    ledger_signal: str,
    answer_delta_specificity: str = "missing_or_unclear",
) -> dict[str, object]:
    return {
        "would_unlock_redesigned_policy": ledger_signal == "additive_pressure_present",
        "would_unlock_answer_delta_guarded_policy": (
            ledger_signal == "additive_pressure_present"
            and answer_delta_specificity in UNLOCKING_ANSWER_DELTA_SPECIFICITY
        ),
        "policy_dependency": (
            "cache_hit plus additive Step 6 ledger plus preserved payload can make "
            "deck-aware output visible; this replay only tests the ledger dependency."
        ),
        "answer_delta_dependency": (
            "The answer-delta guarded policy additionally requires Step 6 to name "
            "a concrete or specific structural visible-answer delta."
        ),
    }


def _validate_input_packet(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: input_packet must be an object"
        return
    yield from _unknown_fields(value, INPUT_PACKET_FIELDS, path)
    yield from _missing_fields(value, tuple(INPUT_PACKET_FIELDS), path)
    if any(field not in value for field in INPUT_PACKET_FIELDS):
        return
    for field in (
        "case_brief",
        "pre_run_failure_hypothesis",
        "anchor_visible_candidate",
        "deck_pressure_candidate",
    ):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    for field in ("expected_deck_adds", "anchor_risk_if_hidden"):
        if not _non_empty_string_list(value.get(field)):
            yield f"{path / field}: must be a non-empty string list"


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


def _validate_step6_output(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: step6_output must be an object"
        return
    yield from _unknown_fields(value, STEP6_OUTPUT_FIELDS, path)
    yield from _missing_fields(value, tuple(STEP6_OUTPUT_FIELDS), path)
    if any(field not in value for field in STEP6_OUTPUT_FIELDS):
        return
    answer_core = _string(value.get("answer_core"))
    if not answer_core.strip():
        yield f"{path / 'answer_core'}: must be non-empty"
    else:
        try:
            validate_public_answer_hygiene(answer_core)
        except ValueError as exc:
            yield f"{path / 'answer_core'}: {exc}"
        lowered = answer_core.lower()
        for term in PRIVATE_LABEL_TERMS:
            if term in lowered:
                yield f"{path / 'answer_core'}: private label leaked: {term}"
    yield from _validate_ledger(
        value.get("private_bridge_consideration_ledger"),
        path / "private_bridge_consideration_ledger",
    )


def _validate_ledger(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: private_bridge_consideration_ledger must be a list"
        return
    ids = [_string(item.get("source_id")) if isinstance(item, dict) else "" for item in value]
    if tuple(ids) != ALLOWED_SOURCE_IDS:
        yield f"{path}: ledger must account for anchor_visible_candidate and deck_pressure_candidate"
    for index, item in enumerate(value):
        item_path = path / f"[{index}]"
        if not isinstance(item, dict):
            yield f"{item_path}: ledger item must be an object"
            continue
        yield from _unknown_fields(item, LEDGER_FIELDS, item_path)
        yield from _missing_fields(item, tuple(LEDGER_REQUIRED_FIELDS), item_path)
        if any(field not in item for field in LEDGER_REQUIRED_FIELDS):
            continue
        if _string(item.get("source_id")) not in ALLOWED_SOURCE_IDS:
            yield f"{item_path / 'source_id'}: unknown source_id"
        if _string(item.get("disposition")) not in ALLOWED_DISPOSITIONS:
            yield f"{item_path / 'disposition'}: unknown disposition"
        if _string(item.get("novelty_role")) not in ALLOWED_NOVELTY_ROLES:
            yield f"{item_path / 'novelty_role'}: unknown novelty_role"
        for field in ("why", "visible_effect"):
            if not _string(item.get(field)).strip():
                yield f"{item_path / field}: must be non-empty"
        if "answer_delta" in item:
            yield from _validate_answer_delta(item.get("answer_delta"), item_path / "answer_delta")


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
        if field not in value:
            continue
        if not isinstance(value[field], list):
            yield f"{path / field}: must be a list of strings"
            continue
        for index, item in enumerate(value[field]):
            if not isinstance(item, str) or not item.strip():
                yield f"{path / field / str(index)}: must be a non-empty string"


def _validate_visibility_read(
    value: object,
    path: Path,
    *,
    ledger_signal: str,
    answer_delta_specificity: str,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: visibility_redesign_read must be an object"
        return
    yield from _unknown_fields(value, VISIBILITY_READ_FIELDS, path)
    yield from _missing_fields(value, tuple(VISIBILITY_READ_REQUIRED_FIELDS), path)
    if any(field not in value for field in VISIBILITY_READ_REQUIRED_FIELDS):
        return
    expected = ledger_signal == "additive_pressure_present"
    if value.get("would_unlock_redesigned_policy") is not expected:
        yield f"{path / 'would_unlock_redesigned_policy'}: must follow ledger_signal"
    if "would_unlock_answer_delta_guarded_policy" in value:
        expected_delta = expected and answer_delta_specificity in UNLOCKING_ANSWER_DELTA_SPECIFICITY
        if value.get("would_unlock_answer_delta_guarded_policy") is not expected_delta:
            yield (
                f"{path / 'would_unlock_answer_delta_guarded_policy'}: "
                "must follow ledger_signal and answer_delta_specificity"
            )
    dependency = _string(value.get("policy_dependency")).lower()
    if "preserved payload" not in dependency or "only tests the ledger" not in dependency:
        yield f"{path / 'policy_dependency'}: must state replay scope"
    if "answer_delta_dependency" in value and "visible-answer delta" not in _string(
        value.get("answer_delta_dependency")
    ).lower():
        yield f"{path / 'answer_delta_dependency'}: must state answer_delta dependency"


def _validate_case_result(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: case result must be an object"
        return
    yield from _unknown_fields(value, CASE_RESULT_FIELDS, path)
    required = tuple(CASE_RESULT_FIELDS - OPTIONAL_CASE_RESULT_FIELDS)
    yield from _missing_fields(value, required, path)
    if any(field not in value for field in required):
        return
    if not _string(value.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    if _string(value.get("ledger_signal")) not in ALLOWED_LEDGER_SIGNALS:
        yield f"{path / 'ledger_signal'}: unknown ledger_signal"
    expected = value.get("ledger_signal") == "additive_pressure_present"
    if value.get("would_unlock_redesigned_policy") is not expected:
        yield f"{path / 'would_unlock_redesigned_policy'}: must follow ledger_signal"
    if "answer_delta_specificity" in value and _string(
        value.get("answer_delta_specificity")
    ) not in ALLOWED_ANSWER_DELTA_SPECIFICITY:
        yield f"{path / 'answer_delta_specificity'}: unknown answer_delta_specificity"
    if "would_unlock_answer_delta_guarded_policy" in value:
        expected_delta = (
            expected
            and value.get("answer_delta_specificity") in UNLOCKING_ANSWER_DELTA_SPECIFICITY
        )
        if value.get("would_unlock_answer_delta_guarded_policy") is not expected_delta:
            yield (
                f"{path / 'would_unlock_answer_delta_guarded_policy'}: "
                "must follow ledger_signal and answer_delta_specificity"
            )


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


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(
    payload: dict[str, object],
    required: Sequence[str],
    path: Path,
) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path / field}: missing required field"


def _non_empty_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


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


def _normalize_answer_delta(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        value = {}
    return {
        field: [
            item.strip()
            for item in value.get(field, [])
            if isinstance(item, str) and item.strip()
        ]
        for field in sorted(ANSWER_DELTA_FIELDS)
    }


def _empty_answer_delta() -> dict[str, list[str]]:
    return {field: [] for field in sorted(ANSWER_DELTA_FIELDS)}


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


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


def _load_env_file(path: Path) -> None:
    if not path.exists():
        raise BridgeStep6LedgerReplayValidationError(f"env file missing: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--contract", type=Path, default=Path(DEFAULT_CONTRACT_REF))
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", default="")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            if path.name.endswith("bridge-step6-ledger-replay-result.v1.json"):
                validate_bridge_step6_replay_result(load_bridge_step6_replay_result(path), path=path)
            else:
                validate_bridge_step6_replay_payload(load_bridge_step6_replay_payload(path), path=path)
        return 0

    from pre_step6_false_standdown_bridge_probe import load_bridge_probe_contract

    contract = load_bridge_probe_contract(args.contract)
    if args.live:
        case_ids = _parse_case_ids(args, contract)
        output_paths = []
        for case_id in case_ids:
            output = run_live_replay(
                contract=contract,
                case_id=case_id,
                provider=args.provider,
                model=args.model,
                env_file=args.env_file,
                out_dir=args.out_dir,
                dry_run=args.dry_run,
            )
            if output is not None:
                output_paths.append(output)
                print(output)
        if output_paths:
            replays = [load_bridge_step6_replay_payload(path) for path in output_paths]
            result = build_bridge_step6_replay_result(replays=replays)
            print(write_bridge_step6_replay_result(payload=result, out_dir=args.out_dir))
        return 0

    for path in write_fixture_suite(contract=contract, out_dir=args.out_dir):
        print(path)
    return 0


def _parse_case_ids(args: argparse.Namespace, contract: dict[str, object]) -> list[str]:
    if args.all:
        cases = contract.get("probe_cases")
        if not isinstance(cases, list):
            raise BridgeStep6LedgerReplayValidationError("probe_cases missing")
        return [_string(case.get("case_id")) for case in cases if isinstance(case, dict)]
    if args.case_id:
        return args.case_id
    raise BridgeStep6LedgerReplayValidationError("provide --case-id or --all for live replay")


if __name__ == "__main__":
    raise SystemExit(main())
