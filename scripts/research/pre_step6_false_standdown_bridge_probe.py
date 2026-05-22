#!/usr/bin/env python3
"""Research-only false-standdown bridge probe.

The probe tests the dangerous corner before full calibration: cases where a
runtime anchor-biased public policy might suppress deck pressure that a
cognitive reviewer later judges material. It is non-promotional by design.
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


CONTRACT_SCHEMA_VERSION = "pre_step6_false_standdown_bridge_probe.v1"
JUDGMENT_SCHEMA_VERSION = "pre_step6_false_standdown_bridge_judgment.v1"
RESULT_SCHEMA_VERSION = "pre_step6_false_standdown_bridge_result.v1"
STATUS = "planned_non_promotional"
JUDGMENT_STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
PROBE_ID = "false_standdown_bridge_probe_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-false-standdown-bridge-probe")
DEFAULT_JUDGMENT_DIR = DEFAULT_OUT_DIR / "judgments"
DEFAULT_SEED = 2026052101
ALLOWED_STANDDOWN_LABELS = frozenset(
    {"true_standdown", "false_standdown", "ambiguous_standdown", "not_observed"}
)
ALLOWED_WINNER_ARMS = frozenset({"anchor_visible", "deck_visible", "tie"})
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
        "probe_cases",
        "gates",
        "notes",
    }
)
CONFIRMATION_FIELDS = frozenset(
    {"confirmed_false_standdown", "single_reviewer_false_standdown", "human_spot_check_only"}
)
REVIEWER_RULE_FIELDS = frozenset(
    {"reviewer_count", "model_family_policy", "prompt_policy", "blind_shuffle_policy"}
)
CASE_FIELDS = frozenset(
    {
        "case_id",
        "shape_id",
        "selection_timing",
        "case_brief",
        "pre_run_failure_hypothesis",
        "expected_deck_adds",
        "anchor_risk_if_hidden",
        "answer_candidates",
    }
)
CANDIDATE_FIELDS = frozenset({"anchor_visible", "deck_visible"})
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
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
REVIEWER_OUTPUT_FIELDS = frozenset(
    {
        "standdown_label",
        "winner_label",
        "confidence",
        "expected_failure_observed",
        "rationale",
        "anchor_missing_payload",
        "deck_added_payload",
        "regressions_or_bloat",
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
        "reviewer_count",
        "reviewer_model_families",
        "standdown_labels",
        "confirmed_label",
        "stop_condition_triggered",
    }
)
CONFIRMED_RULE_TEXT = (
    "Two reviewer judgments label the same case false_standdown under "
    "the same rubric, fresh blind shuffles, and different model families."
)


class FalseStanddownBridgeProbeError(ValueError):
    pass


def build_bridge_probe_contract() -> dict[str, object]:
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "probe_id": PROBE_ID,
        "status": STATUS,
        "promotion_effect": "none_bridge_only",
        "stop_condition": (
            "Any confirmed false_standdown triggers design review before an "
            "integration draft."
        ),
        "confirmation_rule": {
            "confirmed_false_standdown": CONFIRMED_RULE_TEXT,
            "single_reviewer_false_standdown": "not_confirmed",
            "human_spot_check_only": "not_confirmed",
        },
        "reviewer_rule": {
            "reviewer_count": 2,
            "model_family_policy": "different_model_family_required",
            "prompt_policy": "same_rubric",
            "blind_shuffle_policy": "fresh_blind_shuffle_per_reviewer",
        },
        "probe_cases": _probe_cases(),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only bridge probe. Probe-case failure hypotheses are "
            "pre-registered before reviewer judgments are generated."
        ),
    }
    validate_bridge_probe_contract(payload)
    return payload


def load_bridge_probe_contract(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise FalseStanddownBridgeProbeError(f"{path}: payload must be an object")
    return payload


def validate_bridge_probe_contract(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_bridge_probe_contract_errors(payload, path=Path(path)))
    if errors:
        raise FalseStanddownBridgeProbeError("; ".join(errors))


def validate_bridge_probe_contract_file(path: Path) -> None:
    validate_bridge_probe_contract(load_bridge_probe_contract(path), path=Path(path))


def iter_bridge_probe_contract_errors(
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
    if not _string(payload.get("stop_condition")).startswith("Any confirmed false_standdown"):
        yield f"{path / 'stop_condition'}: must be consequential"
    yield from _validate_confirmation_rule(payload.get("confirmation_rule"), path / "confirmation_rule")
    yield from _validate_reviewer_rule(payload.get("reviewer_rule"), path / "reviewer_rule")
    yield from _validate_probe_cases(payload.get("probe_cases"), path / "probe_cases")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def write_bridge_probe_contract(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_bridge_probe_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "false-standdown-bridge-probe.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def build_reviewer_packet(
    *,
    contract: dict[str, object],
    case_id: str,
    seed: int = DEFAULT_SEED,
) -> dict[str, object]:
    validate_bridge_probe_contract(contract)
    case = _case_by_id(contract, case_id)
    answers = case["answer_candidates"]
    assert isinstance(answers, dict)
    arms = ["anchor_visible", "deck_visible"]
    rng = random.Random(seed + sum(ord(char) for char in case_id))
    rng.shuffle(arms)
    blind_map = dict(zip(("A", "B"), arms, strict=True))
    candidates = {
        label: {
            "answer_core": _string(answers[arm]),
            "char_count": len(_string(answers[arm])),
        }
        for label, arm in blind_map.items()
    }
    return {
        "probe_id": PROBE_ID,
        "case_id": case_id,
        "case_brief": case["case_brief"],
        "pre_run_failure_hypothesis": case["pre_run_failure_hypothesis"],
        "expected_deck_adds": case["expected_deck_adds"],
        "anchor_risk_if_hidden": case["anchor_risk_if_hidden"],
        "reviewer_task": (
            "A runtime anchor-biased policy would keep the anchor-visible answer "
            "public and keep the deck-visible pressure private if unresolved. "
            "Label this stand-down. false_standdown means the deck-visible answer "
            "is materially better because it preserves the pre-registered missing "
            "pressure. true_standdown means the anchor is better or the deck adds "
            "no material value. ambiguous_standdown means mixed or unclear. "
            "not_observed means the packet is insufficient."
        ),
        "candidates_by_label": candidates,
        "blind_map_private": blind_map,
        "response_schema": {
            "standdown_label": "true_standdown | false_standdown | ambiguous_standdown | not_observed",
            "winner_label": "A | B | tie",
            "confidence": "high | medium | low",
            "expected_failure_observed": "true | false",
            "rationale": "Short rationale.",
            "anchor_missing_payload": ["Concrete anchor omissions, if any."],
            "deck_added_payload": ["Concrete deck additions, if any."],
            "regressions_or_bloat": ["Deck regressions or bloat, if any."],
        },
    }


def build_static_reviewer_judgment(
    *,
    contract: dict[str, object],
    case_id: str,
    model: str,
    standdown_label: str,
    winner_arm: str,
) -> dict[str, object]:
    packet = build_reviewer_packet(contract=contract, case_id=case_id)
    blind_map = _string_dict(packet["blind_map_private"])
    winner_label = "tie"
    if winner_arm != "tie":
        winner_label = next(label for label, arm in blind_map.items() if arm == winner_arm)
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "probe_id": PROBE_ID,
        "case_id": case_id,
        "judgment_source": "static_test_reviewer_judgment",
        "provider_metadata": {
            "provider": "static",
            "model": model,
            "model_family": _model_family(model),
            "status": "ok",
        },
        "blind_map": blind_map,
        "reviewer_output": {
            "standdown_label": standdown_label,
            "winner_label": winner_label,
            "confidence": "high",
            "expected_failure_observed": standdown_label == "false_standdown",
            "rationale": "Static fixture judgment.",
            "anchor_missing_payload": ["Static missing payload."],
            "deck_added_payload": ["Static added payload."],
            "regressions_or_bloat": ["none"],
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Static test fixture.",
    }
    validate_bridge_probe_judgment(payload)
    return payload


def load_bridge_probe_judgment(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise FalseStanddownBridgeProbeError(f"{path}: payload must be an object")
    return payload


def validate_bridge_probe_judgment(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_bridge_probe_judgment_errors(payload, path=Path(path)))
    if errors:
        raise FalseStanddownBridgeProbeError("; ".join(errors))


def validate_bridge_probe_judgment_file(path: Path) -> None:
    validate_bridge_probe_judgment(load_bridge_probe_judgment(path), path=Path(path))


def iter_bridge_probe_judgment_errors(
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


def write_bridge_probe_judgment(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_bridge_probe_judgment(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = _string(payload["provider_metadata"]["model"]).replace("/", "__")
    path = out_dir / f"{_string(payload['case_id'])}.{model_slug}.false-standdown-bridge-judgment.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def run_live_reviewer(
    *,
    contract: dict[str, object],
    case_id: str,
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
    packet = build_reviewer_packet(contract=contract, case_id=case_id, seed=seed)
    private_blind_map = _string_dict(packet.pop("blind_map_private"))
    reviewer_packet = dict(packet)
    if dry_run:
        print(json.dumps(reviewer_packet, indent=2, ensure_ascii=False))
        return None
    repo_root = Path.cwd()
    sys.path.insert(0, str(repo_root / "engine"))
    sys.path.insert(0, str(repo_root))
    from system_b.boundary_provider import load_boundary_client_from_env  # noqa: PLC0415

    client = load_boundary_client_from_env(provider)
    output, metadata = client.run_json_with_metadata(
        _system_prompt(),
        json.dumps(reviewer_packet, indent=2, ensure_ascii=False),
        stage="pre_step6_false_standdown_bridge_probe",
        tendency_id=case_id,
    )
    provider_metadata = _provider_metadata_dict(metadata)
    provider_metadata["model_family"] = _model_family(_string(provider_metadata.get("model")))
    if _string(provider_metadata.get("status")) != "ok":
        raise FalseStanddownBridgeProbeError(
            "live false-standdown bridge probe failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "probe_id": PROBE_ID,
        "case_id": case_id,
        "judgment_source": "manual_llm_reviewer_judgment",
        "provider_metadata": provider_metadata,
        "blind_map": private_blind_map,
        "reviewer_output": _normalize_reviewer_output(output, blind_map=private_blind_map),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Live non-promotional false-standdown bridge-probe judgment.",
    }
    return write_bridge_probe_judgment(payload=payload, out_dir=out_dir)


def build_bridge_probe_result(
    *,
    contract: dict[str, object],
    judgments: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_bridge_probe_contract(contract)
    for judgment in judgments:
        validate_bridge_probe_judgment(judgment)
    case_results = []
    by_case: dict[str, list[dict[str, object]]] = {}
    for judgment in judgments:
        by_case.setdefault(_string(judgment.get("case_id")), []).append(judgment)
    for case_id in sorted(by_case):
        case_judgments = by_case[case_id]
        labels = [
            _string(judgment["reviewer_output"]["standdown_label"])
            for judgment in case_judgments
        ]
        families = sorted(
            {
                _string(judgment["provider_metadata"].get("model_family"))
                for judgment in case_judgments
                if _string(judgment["provider_metadata"].get("model_family"))
            }
        )
        confirmed = _confirmed_label(labels=labels, families=families)
        case_results.append(
            {
                "case_id": case_id,
                "reviewer_count": len(case_judgments),
                "reviewer_model_families": families,
                "standdown_labels": labels,
                "confirmed_label": confirmed,
                "stop_condition_triggered": confirmed == "false_standdown",
            }
        )
    any_stop = any(result["stop_condition_triggered"] for result in case_results)
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "runtime_policy": RUNTIME_POLICY,
        "probe_id": PROBE_ID,
        "promotion_effect": "none_bridge_only",
        "case_results": case_results,
        "probe_result": "design_review_required" if any_stop else "continue_bridge_probe",
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Aggregate result for non-promotional false-standdown bridge probe.",
    }
    validate_bridge_probe_result(payload)
    return payload


def load_bridge_probe_result(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise FalseStanddownBridgeProbeError(f"{path}: payload must be an object")
    return payload


def validate_bridge_probe_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_bridge_probe_result_errors(payload, path=Path(path)))
    if errors:
        raise FalseStanddownBridgeProbeError("; ".join(errors))


def validate_bridge_probe_result_file(path: Path) -> None:
    validate_bridge_probe_result(load_bridge_probe_result(path), path=Path(path))


def write_bridge_probe_result(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_bridge_probe_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "false-standdown-bridge-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def iter_bridge_probe_result_errors(
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
        expected = (
            "design_review_required"
            if any(isinstance(result, dict) and result.get("stop_condition_triggered") is True for result in results)
            else "continue_bridge_probe"
        )
        if payload.get("probe_result") != expected:
            yield f"{path / 'probe_result'}: must be {expected}"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def _probe_cases() -> list[dict[str, object]]:
    return [
        {
            "case_id": "bridge-high-clutter-sensitive-overlay",
            "shape_id": "high_clutter_sensitive_overlay",
            "selection_timing": "pre_run",
            "case_brief": (
                "Founder must respond to an anxious early employee who claims an "
                "informal equity promise, while a financing deadline and team "
                "fragility make tone risky."
            ),
            "pre_run_failure_hypothesis": (
                "If runtime shows the anchor because it sounds calmer, but hides "
                "the deck pressure separating empathy from binding equity or "
                "deadline commitments, this is a false stand-down."
            ),
            "expected_deck_adds": [
                "separate the humane check-in from equity commitment",
                "name the evidence threshold before any cap-table promise",
                "protect the financing deadline without turning the employee into the enemy",
            ],
            "anchor_risk_if_hidden": [
                "calm tone may mask an accidental commitment",
                "employee concern and investor deadline may get collapsed into one conversation",
            ],
            "answer_candidates": {
                "anchor_visible": (
                    "Talk to her directly and calmly. Acknowledge that the earlier "
                    "conversation may have created expectations, explain that you "
                    "need to check the facts before making any promise, and set a "
                    "short follow-up. Keep the financing process separate and avoid "
                    "arguing over memory in the first conversation."
                ),
                "deck_visible": (
                    "Do two separate things, in this order. First, have a humane "
                    "conversation that names the concern without conceding the equity "
                    "claim: you will review written notes, emails, and board-approved "
                    "terms before making any cap-table commitment. Second, protect the "
                    "financing deadline by telling investors only what is true now: no "
                    "new grant or correction exists until evidence and board process "
                    "support it. If she has written evidence, inspect it quickly; if "
                    "she only has a memory of an informal promise, offer a bounded "
                    "review path rather than a negotiation under pressure."
                ),
            },
        },
        {
            "case_id": "bridge-sensitive-anchor-misses-tripwire",
            "shape_id": "sensitive_anchor_misses_tripwire",
            "selection_timing": "pre_run",
            "case_brief": (
                "Parent found a minor child in secret contact with an older online "
                "person. The safe answer must keep tone humane while preserving "
                "concrete escalation triggers."
            ),
            "pre_run_failure_hypothesis": (
                "If runtime shows the anchor because it is gentler, but hides the "
                "deck's concrete tripwires for escalation, this is a false stand-down."
            ),
            "expected_deck_adds": [
                "explicit tripwires for meeting requests, sexual images, threats, other minors, or migration to hidden channels",
                "professional/legal guidance before irreversible reporting choices",
                "do not treat a quiet monitored phone as proof of safety",
            ],
            "anchor_risk_if_hidden": [
                "gentle tone may become delay without a floor",
                "parent may miss the facts that should override slow repair",
            ],
            "answer_candidates": {
                "anchor_visible": (
                    "Slow the situation down. Talk with a therapist, RAINN, or counsel "
                    "before deciding whether to report, keep your daughter's trust as "
                    "central as safety allows, and avoid a sudden phone shutdown that "
                    "drives contact underground. Tell the co-parent enough to align on "
                    "safety without turning it into a blame fight."
                ),
                "deck_visible": (
                    "Use the slow-repair plan only while the safety floor holds. Talk "
                    "with RAINN, a therapist, or counsel before deciding whether to "
                    "report, and avoid a sudden phone shutdown unless a tripwire fires. "
                    "The tripwires are concrete: a request to meet, sexual images, "
                    "threats, evidence the older person is contacting other minors, "
                    "migration to a hidden channel after boundaries are set, or your "
                    "daughter saying she feels pressured or afraid. Also treat a quiet "
                    "monitored phone as weak evidence, not reassurance; the channel may "
                    "simply have moved."
                ),
            },
        },
        {
            "case_id": "bridge-sequencing-sensitive-boundary",
            "shape_id": "sequencing_sensitive_boundary",
            "selection_timing": "pre_run",
            "case_brief": (
                "PhD student must choose a dissertation direction while advisor "
                "retirement, cross-lab politics, and possible visa/funding constraints "
                "make the sequence sensitive."
            ),
            "pre_run_failure_hypothesis": (
                "If runtime shows the anchor because it is concise, but hides the "
                "deck's sequencing boundary for advisor, collaborator, funding, and "
                "fallback checks, this is a false stand-down."
            ),
            "expected_deck_adds": [
                "advisor support before approaching the outside lab",
                "data-access and funding feasibility before committee commitment",
                "18-month go/no-go checkpoint with fallback",
            ],
            "anchor_risk_if_hidden": [
                "student may create political friction by approaching collaborators too early",
                "ambition may outrun funding and data access checks",
            ],
            "answer_candidates": {
                "anchor_visible": (
                    "Option 3 sounds like the best direction if you can get the data. "
                    "It keeps your existing tumor-evolution strength while connecting "
                    "you to the single-cell field. Talk to the single-cell postdoc, "
                    "test whether the collaboration is real, and fall back to the "
                    "standard lab project if the data path fails."
                ),
                "deck_visible": (
                    "Option 3 is the best candidate, but the order matters. First ask "
                    "your advisor whether he supports the cross-lab direction, whether "
                    "funding covers it, and whether he would accept a real co-advisor. "
                    "Only then approach the single-cell postdoc with a specific methods "
                    "proposal and ask what data access, authorship, and PI approval "
                    "would require. Do not commit with the committee until data access "
                    "and funding are real. Pre-commit now to an 18-month checkpoint: if "
                    "there is no publishable result on the pipeline by then, pivot to a "
                    "narrower tumor-evolution project while you still have time."
                ),
            },
        },
    ]


def _case_by_id(contract: dict[str, object], case_id: str) -> dict[str, object]:
    cases = contract.get("probe_cases")
    if not isinstance(cases, list):
        raise FalseStanddownBridgeProbeError("probe_cases missing")
    for case in cases:
        if isinstance(case, dict) and case.get("case_id") == case_id:
            return case
    raise FalseStanddownBridgeProbeError(f"unknown bridge probe case: {case_id}")


def _validate_confirmation_rule(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, CONFIRMATION_FIELDS, path)
    yield from _missing_fields(value, CONFIRMATION_FIELDS, path)
    expected = {
        "confirmed_false_standdown": CONFIRMED_RULE_TEXT,
        "single_reviewer_false_standdown": "not_confirmed",
        "human_spot_check_only": "not_confirmed",
    }
    if value != expected:
        yield f"{path}: invalid confirmation rule"


def _validate_reviewer_rule(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, REVIEWER_RULE_FIELDS, path)
    yield from _missing_fields(value, REVIEWER_RULE_FIELDS, path)
    if value.get("reviewer_count") != 2:
        yield f"{path / 'reviewer_count'}: must be 2"
    if value.get("model_family_policy") != "different_model_family_required":
        yield f"{path / 'model_family_policy'}: must require different model families"
    if value.get("prompt_policy") != "same_rubric":
        yield f"{path / 'prompt_policy'}: must be same_rubric"
    if value.get("blind_shuffle_policy") != "fresh_blind_shuffle_per_reviewer":
        yield f"{path / 'blind_shuffle_policy'}: must be fresh_blind_shuffle_per_reviewer"


def _validate_probe_cases(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list) or len(value) != 3:
        yield f"{path}: must contain exactly three probe cases"
        return
    shape_ids = []
    for index, case in enumerate(value):
        if not isinstance(case, dict):
            yield f"{path / str(index)}: must be an object"
            continue
        yield from _unknown_fields(case, CASE_FIELDS, path / str(index))
        yield from _missing_fields(case, CASE_FIELDS, path / str(index))
        if case.get("selection_timing") != "pre_run":
            yield f"{path / str(index) / 'selection_timing'}: must be pre_run"
        for field in ("case_id", "shape_id", "case_brief", "pre_run_failure_hypothesis"):
            if not _string(case.get(field)).strip():
                yield f"{path / str(index) / field}: must be non-empty"
        if not _string(case.get("pre_run_failure_hypothesis")).startswith("If runtime shows the anchor"):
            yield f"{path / str(index) / 'pre_run_failure_hypothesis'}: must be pre-run and conditional"
        for field in ("expected_deck_adds", "anchor_risk_if_hidden"):
            if not _string_list(case.get(field)):
                yield f"{path / str(index) / field}: must be a non-empty string list"
        shape_ids.append(_string(case.get("shape_id")))
        yield from _validate_candidates(case.get("answer_candidates"), path / str(index) / "answer_candidates")
    expected_shapes = [
        "high_clutter_sensitive_overlay",
        "sensitive_anchor_misses_tripwire",
        "sequencing_sensitive_boundary",
    ]
    if shape_ids != expected_shapes:
        yield f"{path}: shape order must be {expected_shapes}"


def _validate_candidates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, CANDIDATE_FIELDS, path)
    yield from _missing_fields(value, CANDIDATE_FIELDS, path)
    for field in CANDIDATE_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_provider_metadata(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    if "provider" not in value and "provider_name" not in value:
        yield f"{path}: provider or provider_name is required"
    if not _string(value.get("model")).strip():
        yield f"{path / 'model'}: must be non-empty"
    if not _string(value.get("model_family")).strip():
        yield f"{path / 'model_family'}: must be non-empty"
    if not _string(value.get("status")).strip():
        yield f"{path / 'status'}: must be non-empty"
    for field in sorted(set(value) - PROVIDER_METADATA_FIELDS):
        yield f"{path / field}: unknown field"


class _BlindMapResult:
    def __init__(self, value: dict[str, str], errors: list[str]) -> None:
        self.value = value
        self.errors = errors


def _validate_blind_map(value: object, path: Path) -> _BlindMapResult:
    if not isinstance(value, dict):
        return _BlindMapResult({}, [f"{path}: must be an object"])
    result = {str(key): str(map_value) for key, map_value in value.items()}
    errors = []
    if set(result) != {"A", "B"}:
        errors.append(f"{path}: must contain A and B")
    if set(result.values()) != {"anchor_visible", "deck_visible"}:
        errors.append(f"{path}: must map to anchor_visible and deck_visible")
    return _BlindMapResult(result, errors)


def _validate_reviewer_output(
    value: object,
    *,
    blind_map: dict[str, str],
    path: Path,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, REVIEWER_OUTPUT_FIELDS, path)
    yield from _missing_fields(value, REVIEWER_OUTPUT_FIELDS, path)
    if any(field not in value for field in REVIEWER_OUTPUT_FIELDS):
        return
    if value.get("standdown_label") not in ALLOWED_STANDDOWN_LABELS:
        yield f"{path / 'standdown_label'}: unsupported label"
    winner = _string(value.get("winner_label"))
    if winner not in {"A", "B", "tie"}:
        yield f"{path / 'winner_label'}: unsupported label"
    if _winner_arm(winner=winner, blind_map=blind_map) not in ALLOWED_WINNER_ARMS:
        yield f"{path / 'winner_label'}: invalid winner arm"
    if _string(value.get("confidence")) not in {"high", "medium", "low"}:
        yield f"{path / 'confidence'}: unsupported confidence"
    if not isinstance(value.get("expected_failure_observed"), bool):
        yield f"{path / 'expected_failure_observed'}: must be boolean"
    for field in ("rationale",):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    for field in ("anchor_missing_payload", "deck_added_payload", "regressions_or_bloat"):
        if not _string_list(value.get(field)):
            yield f"{path / field}: must be a non-empty string list"
    if value.get("standdown_label") == "false_standdown":
        if _winner_arm(winner=winner, blind_map=blind_map) != "deck_visible":
            yield f"{path / 'standdown_label'}: false_standdown requires deck_visible winner"
        if value.get("expected_failure_observed") is not True:
            yield f"{path / 'expected_failure_observed'}: false_standdown requires true"


def _validate_case_result(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, CASE_RESULT_FIELDS, path)
    yield from _missing_fields(value, CASE_RESULT_FIELDS, path)
    if any(field not in value for field in CASE_RESULT_FIELDS):
        return
    if not _string(value.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    if not isinstance(value.get("reviewer_count"), int):
        yield f"{path / 'reviewer_count'}: must be integer"
    if not _string_list(value.get("reviewer_model_families")):
        yield f"{path / 'reviewer_model_families'}: must be non-empty string list"
    labels = value.get("standdown_labels")
    if not isinstance(labels, list) or any(label not in ALLOWED_STANDDOWN_LABELS for label in labels):
        yield f"{path / 'standdown_labels'}: invalid labels"
    if value.get("confirmed_label") not in ALLOWED_STANDDOWN_LABELS:
        yield f"{path / 'confirmed_label'}: invalid label"
    if not isinstance(value.get("stop_condition_triggered"), bool):
        yield f"{path / 'stop_condition_triggered'}: must be boolean"


def _validate_gates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, GATE_FIELDS, path)
    if value.get("runtime_wiring_allowed") is not False:
        yield f"{path / 'runtime_wiring_allowed'}: must be false"
    if value.get("skill_update_allowed") is not False:
        yield f"{path / 'skill_update_allowed'}: must be false"


def _confirmed_label(*, labels: list[str], families: list[str]) -> str:
    if len(labels) >= 2 and len(families) >= 2 and all(label == "false_standdown" for label in labels):
        return "false_standdown"
    if len(labels) >= 2 and len(set(labels)) == 1 and labels[0] in {
        "true_standdown",
        "not_observed",
    }:
        return labels[0]
    return "ambiguous_standdown"


def _normalize_reviewer_output(value: object, *, blind_map: dict[str, str]) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    winner = _string(value.get("winner_label")) or "tie"
    label = _string(value.get("standdown_label")) or _label_from_winner(winner=winner, blind_map=blind_map)
    normalized = {
        "standdown_label": label,
        "winner_label": winner,
        "confidence": _string(value.get("confidence")) or "low",
        "expected_failure_observed": _bool(value.get("expected_failure_observed")),
        "rationale": _string(value.get("rationale")) or "Reviewer returned no rationale.",
        "anchor_missing_payload": _string_list(value.get("anchor_missing_payload"))
        or ["Reviewer returned no anchor-missing payload."],
        "deck_added_payload": _string_list(value.get("deck_added_payload"))
        or ["Reviewer returned no deck-added payload."],
        "regressions_or_bloat": _string_list(value.get("regressions_or_bloat"))
        or ["Reviewer returned no regressions or bloat."],
    }
    if normalized["standdown_label"] == "false_standdown":
        normalized["expected_failure_observed"] = True
    return normalized


def _label_from_winner(*, winner: str, blind_map: dict[str, str]) -> str:
    arm = _winner_arm(winner=winner, blind_map=blind_map)
    if arm == "deck_visible":
        return "false_standdown"
    if arm == "anchor_visible":
        return "true_standdown"
    return "ambiguous_standdown"


def _winner_arm(*, winner: str, blind_map: dict[str, str]) -> str:
    if winner == "tie":
        return "tie"
    return blind_map.get(winner, "")


def _system_prompt() -> str:
    return (
        "You are a research reviewer for a non-promotional false-standdown probe. "
        "Use only the packet. Do not solve the underlying case from scratch. "
        "Classify whether hiding the deck-visible candidate in favor of the "
        "anchor-visible candidate would be a true_standdown, false_standdown, "
        "ambiguous_standdown, or not_observed. A false_standdown requires that "
        "the deck-visible candidate materially preserves the pre-registered "
        "missing pressure and is visibly better. Return strict JSON only."
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
    if "model_family" not in result:
        result["model_family"] = _model_family(_string(result.get("model")))
    return result


def _model_family(model: str) -> str:
    if "/" in model:
        return model.split("/", 1)[0]
    if "-" in model:
        return model.split("-", 1)[0]
    return model or "unknown"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        raise FalseStanddownBridgeProbeError(f"env file missing: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _unknown_fields(value: dict[str, object], allowed: frozenset[str], path: Path) -> Iterable[str]:
    for field in sorted(set(value) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(value: dict[str, object], required: Iterable[str], path: Path) -> Iterable[str]:
    for field in sorted(set(required) - set(value)):
        yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


def _string_dict(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(map_value) for key, map_value in value.items()}


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Existing contract/judgment/result payloads to validate")
    parser.add_argument("--write-contract", action="store_true")
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", action="append", default=[])
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--judgment-dir", type=Path, default=DEFAULT_JUDGMENT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _validate_path(path: Path) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    schema = payload.get("schema_version") if isinstance(payload, dict) else ""
    if schema == CONTRACT_SCHEMA_VERSION:
        validate_bridge_probe_contract(payload, path=path)
    elif schema == JUDGMENT_SCHEMA_VERSION:
        validate_bridge_probe_judgment(payload, path=path)
    elif schema == RESULT_SCHEMA_VERSION:
        validate_bridge_probe_result(payload, path=path)
    else:
        raise FalseStanddownBridgeProbeError(f"{path}: unknown schema_version")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.paths:
        for path in args.paths:
            _validate_path(path)
        return 0
    contract = (
        load_bridge_probe_contract(args.contract)
        if args.contract is not None
        else build_bridge_probe_contract()
    )
    if args.write_contract:
        print(write_bridge_probe_contract(payload=contract, out_dir=args.out_dir))
        return 0
    case_ids = args.case_id or [case["case_id"] for case in contract["probe_cases"]]
    models = args.model
    if not models:
        raise FalseStanddownBridgeProbeError("provide at least one --model, or use --write-contract")
    outputs: list[Path] = []
    for case_id in case_ids:
        for index, model in enumerate(models):
            output = run_live_reviewer(
                contract=contract,
                case_id=case_id,
                provider=args.provider,
                model=model,
                env_file=args.env_file,
                out_dir=args.judgment_dir,
                seed=args.seed + index,
                dry_run=args.dry_run,
            )
            if output is not None:
                outputs.append(output)
                print(output)
    if outputs:
        judgments = [load_bridge_probe_judgment(path) for path in outputs]
        result = build_bridge_probe_result(contract=contract, judgments=judgments)
        print(write_bridge_probe_result(payload=result, out_dir=args.out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
