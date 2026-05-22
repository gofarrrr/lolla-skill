#!/usr/bin/env python3
"""Research-only live gate for composed private Step 6 context packets."""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import random
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_cognitive_gate_live import CASE_CONFIGS, CognitiveGateValidationError


SCHEMA_VERSION = "pre_step6_context_composition_gate_judgment.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
GATE_KIND = "live_context_composition_comparison"
JUDGMENT_SOURCE = "manual_llm_reviewer_judgment"
DEFAULT_OUT_DIR = Path("research/pre-step6-context-composition-gate-judgments")
DEFAULT_SEED = 2026052002
ARMS = (
    "rendered_only",
    "rendered_plus_bevelin_receipts",
    "rendered_plus_polya_receipts",
    "rendered_plus_dual_receipts",
)
ALLOWED_LABELS = frozenset({"A", "B", "C", "D", "tie"})
ALLOWED_ACTIONS = frozenset({"expand_replay", "retest", "stop"})
ALLOWED_CONFIDENCE = frozenset({"high", "medium", "low"})
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "gate_kind",
        "judgment_source",
        "provider_metadata",
        "candidate_refs",
        "blind_map",
        "reviewer_output",
        "static_expectation",
        "agreement",
        "gates",
        "notes",
    }
)
REVIEWER_OUTPUT_FIELDS = frozenset(
    {
        "winner_label",
        "research_action",
        "confidence",
        "rationale",
        "protected_value",
        "bloat_or_pruning_risk",
        "composition_note",
    }
)
STATIC_EXPECTATION_FIELDS = frozenset(
    {"allowed_winner_arms", "allowed_research_actions"}
)
AGREEMENT_FIELDS = frozenset(
    {"winner_matches_static", "action_matches_static", "overall_match"}
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
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


STATIC_EXPECTATIONS: dict[str, dict[str, list[str]]] = {
    "founder-grant-marcus-equity.high-clutter": {
        "allowed_winner_arms": [
            "rendered_plus_bevelin_receipts",
            "rendered_plus_dual_receipts",
        ],
        "allowed_research_actions": ["expand_replay"],
    },
    "third-year-phd-student.v2": {
        "allowed_winner_arms": [
            "rendered_plus_bevelin_receipts",
            "rendered_plus_polya_receipts",
            "rendered_plus_dual_receipts",
        ],
        "allowed_research_actions": ["expand_replay"],
    },
    "mid-level-consultant-report-2": {
        "allowed_winner_arms": ["rendered_only"],
        "allowed_research_actions": ["stop"],
    },
    "mother-address-year": {
        "allowed_winner_arms": [
            "rendered_only",
            "rendered_plus_polya_receipts",
            "rendered_plus_dual_receipts",
            "tie",
        ],
        "allowed_research_actions": ["retest", "stop"],
    },
}


class ContextCompositionValidationError(ValueError):
    pass


def build_composition_packet(
    *,
    case_id: str,
    repo_root: Path,
    seed: int = DEFAULT_SEED,
) -> dict[str, object]:
    config = _case_config(case_id)
    refs = _candidate_refs(config)
    rendered = _load_json(repo_root / refs["rendered_hybrid"])
    bevelin = _load_json(repo_root / refs["bevelin_lens"])
    polya = _load_json(repo_root / refs["polya_lens"])

    arm_packets = {
        "rendered_only": _compose_context_packet(
            primary_anchor=_answer_core(rendered),
            protected_receipts=[],
        ),
        "rendered_plus_bevelin_receipts": _compose_context_packet(
            primary_anchor=_answer_core(rendered),
            protected_receipts=_lens_receipts(bevelin),
        ),
        "rendered_plus_polya_receipts": _compose_context_packet(
            primary_anchor=_answer_core(rendered),
            protected_receipts=_lens_receipts(polya),
        ),
        "rendered_plus_dual_receipts": _compose_context_packet(
            primary_anchor=_answer_core(rendered),
            protected_receipts=_dedupe_strings(
                [*_lens_receipts(bevelin), *_lens_receipts(polya)]
            ),
        ),
    }

    arms = list(ARMS)
    rng = random.Random(seed + sum(ord(char) for char in case_id))
    rng.shuffle(arms)
    labels = ("A", "B", "C", "D")
    blind_map = dict(zip(labels, arms, strict=True))
    candidates_by_label = {
        label: {
            "context_packet": arm_packets[arm],
            "char_count": len(arm_packets[arm]),
        }
        for label, arm in blind_map.items()
    }
    return {
        "case_id": case_id,
        "seed": seed,
        "gate_kind": GATE_KIND,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "reviewer_instruction": _reviewer_instruction(),
        "candidates_by_label": candidates_by_label,
        "candidate_refs": refs,
        "blind_map": blind_map,
        "response_schema": _response_schema(),
        "policy": {
            "do_not_write_a_final_answer": True,
            "compare_private_context_packets_only": True,
            "prefer_enrichment_over_premature_pruning": True,
            "protect_receipts_without_forcing_step6_to_use_them": True,
            "stand_down_when_receipts_add_bloat_without_new_quality": True,
        },
    }


def build_reviewer_packet(packet: dict[str, object]) -> dict[str, object]:
    allowed = {
        "case_id",
        "gate_kind",
        "status",
        "runtime_policy",
        "reviewer_instruction",
        "candidates_by_label",
        "response_schema",
        "policy",
    }
    return {key: value for key, value in packet.items() if key in allowed}


def build_composition_gate_judgment_payload(
    *,
    packet: dict[str, object],
    reviewer_output: dict[str, object],
    provider_metadata: dict[str, object],
    notes: str = "",
) -> dict[str, object]:
    static_expectation = _static_expectation(_string(packet.get("case_id")))
    agreement = _score_agreement(
        reviewer_output=reviewer_output,
        blind_map=_blind_map(packet.get("blind_map")),
        static_expectation=static_expectation,
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "case_id": _string(packet.get("case_id")),
        "gate_kind": GATE_KIND,
        "judgment_source": JUDGMENT_SOURCE,
        "provider_metadata": provider_metadata,
        "candidate_refs": _candidate_refs_from_packet(packet),
        "blind_map": _blind_map(packet.get("blind_map")),
        "reviewer_output": reviewer_output,
        "static_expectation": static_expectation,
        "agreement": agreement,
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": notes,
    }
    validate_composition_gate_judgment_payload(payload)
    return payload


def load_composition_gate_judgment_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ContextCompositionValidationError(f"{path}: payload must be an object")
    return payload


def validate_composition_gate_judgment_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_composition_gate_judgment_errors(payload, path=Path(path)))
    if errors:
        raise ContextCompositionValidationError("; ".join(errors))


def validate_composition_gate_judgment_file(path: Path) -> None:
    validate_composition_gate_judgment_payload(
        load_composition_gate_judgment_payload(path),
        path=Path(path),
    )


def iter_composition_gate_judgment_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "gate_kind",
        "judgment_source",
        "provider_metadata",
        "candidate_refs",
        "blind_map",
        "reviewer_output",
        "static_expectation",
        "agreement",
        "gates",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return

    if _string(payload.get("schema_version")) != SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {SCHEMA_VERSION}"
    if _string(payload.get("status")) != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if _string(payload.get("runtime_policy")) != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if _string(payload.get("case_id")) not in STATIC_EXPECTATIONS:
        yield f"{path / 'case_id'}: unknown fixed-suite case"
    if _string(payload.get("gate_kind")) != GATE_KIND:
        yield f"{path / 'gate_kind'}: must be {GATE_KIND}"
    if _string(payload.get("judgment_source")) != JUDGMENT_SOURCE:
        yield f"{path / 'judgment_source'}: must be {JUDGMENT_SOURCE}"

    yield from _validate_provider_metadata(
        payload.get("provider_metadata"),
        path / "provider_metadata",
    )
    yield from _validate_candidate_refs(
        payload.get("candidate_refs"),
        path / "candidate_refs",
    )
    blind_map = _validate_blind_map(payload.get("blind_map"), path / "blind_map")
    reviewer_output = _validate_reviewer_output(
        payload.get("reviewer_output"),
        blind_map=blind_map,
        path=path / "reviewer_output",
    )
    static_expectation = _validate_static_expectation(
        payload.get("static_expectation"),
        path / "static_expectation",
    )
    yield from blind_map.errors
    yield from reviewer_output.errors
    yield from static_expectation.errors

    if (
        not blind_map.errors
        and not reviewer_output.errors
        and not static_expectation.errors
    ):
        expected = _score_agreement(
            reviewer_output=reviewer_output.value,
            blind_map=blind_map.value,
            static_expectation=static_expectation.value,
        )
        yield from _validate_agreement(
            payload.get("agreement"),
            expected=expected,
            path=path / "agreement",
        )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def run_live_gate(
    *,
    case_id: str,
    repo_root: Path,
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
    packet = build_composition_packet(case_id=case_id, repo_root=repo_root, seed=seed)
    reviewer_packet = build_reviewer_packet(packet)
    if dry_run:
        print(json.dumps(reviewer_packet, indent=2, ensure_ascii=False))
        return None

    sys.path.insert(0, str(repo_root / "engine"))
    sys.path.insert(0, str(repo_root))
    from system_b.boundary_provider import load_boundary_client_from_env  # noqa: PLC0415

    client = load_boundary_client_from_env(provider)
    reviewer_output, metadata = client.run_json_with_metadata(
        _system_prompt(),
        json.dumps(reviewer_packet, indent=2, ensure_ascii=False),
        stage="pre_step6_context_composition_gate",
        tendency_id=case_id,
    )
    provider_metadata = _provider_metadata_dict(metadata)
    if _string(provider_metadata.get("status")) != "ok":
        raise ContextCompositionValidationError(
            "live reviewer call failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    if not reviewer_output:
        raise ContextCompositionValidationError("live reviewer returned an empty payload")
    payload = build_composition_gate_judgment_payload(
        packet=packet,
        reviewer_output=_normalize_reviewer_output(reviewer_output),
        provider_metadata=provider_metadata,
        notes=(
            "Live context-composition comparison. Research-only artifact; it tests "
            "whether protected private receipts improve a rendered-hybrid anchor."
        ),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_slug = _string(_case_config(case_id).get("artifact_slug")) or case_id
    out_path = out_dir / f"{artifact_slug}.context-composition-gate.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    validate_composition_gate_judgment_file(out_path)
    return out_path


def _compose_context_packet(
    *,
    primary_anchor: str,
    protected_receipts: list[str],
) -> str:
    parts = [
        "Private Step 6 context packet.",
        "Do not output this structure. Use it only as cognitive input.",
        "",
        "Primary answer anchor:",
        primary_anchor.strip(),
    ]
    if protected_receipts:
        parts.extend(
            [
                "",
                "Protected enrichment receipts:",
                *[f"- {receipt.strip()}" for receipt in protected_receipts],
                "",
                "Receipt handling rule:",
                (
                    "These receipts are not obligations. Step 6 may use, ignore, or "
                    "combine them, but they are protected so useful edge pressure is "
                    "not pruned before reasoning. The smallest sufficient packet "
                    "wins: each extra receipt carries a complexity tax unless it adds "
                    "novel decision pressure."
                ),
            ]
        )
    else:
        parts.extend(
            [
                "",
                "Protected enrichment receipts:",
                "- None. Use only the primary anchor unless Step 6 independently needs more.",
            ]
        )
    return "\n".join(parts)


def _lens_receipts(payload: dict[str, object]) -> list[str]:
    effect = payload.get("lens_effect")
    if not isinstance(effect, dict):
        return []
    changed = _string_list(effect.get("changed_by_lens"))
    preserved = _string_list(effect.get("preserved_from_base"))
    receipts = [*changed, *preserved[:2]]
    return _dedupe_strings(receipts)


def _reviewer_instruction() -> str:
    return (
        "Compare the blinded private Step 6 context packets. Do not write the "
        "final user answer. Do not judge which candidate is the best final answer "
        "or prose template. Judge which packet gives Step 6 the best cognitive "
        "input while preserving breadth, depth, and useful edge pressure. Receipts "
        "are protected context, not commands. Reward receipts only when they add "
        "quality without forcing premature closure or bloat. The smallest sufficient "
        "packet wins: each extra receipt carries a complexity tax unless it adds "
        "novel decision pressure. research_action "
        "applies to the composed context layer: expand_replay means protected "
        "receipts clearly improve the anchor and deserve more replay testing; "
        "retest means useful but not decisive; stop means rendered-only should "
        "stand for this case. Return only JSON matching response_schema."
    )


def _system_prompt() -> str:
    return (
        "You are a cognitive comparison gate for research-only private Step 6 "
        "context packets. Your job is not final answer generation and not a prose "
        "beauty contest. Choose the packet that best equips a later Step 6 answer "
        "to reason broadly and concretely. Prefer protected useful receipts over "
        "premature pruning, but apply a complexity tax: the smallest sufficient "
        "packet wins when extra receipts merely restate the anchor. Return strict "
        "JSON only."
    )


def _response_schema() -> dict[str, object]:
    return {
        "winner_label": "A | B | C | D | tie",
        "research_action": "expand_replay | retest | stop",
        "confidence": "high | medium | low",
        "rationale": "Short explanation of the cognitive-context judgment.",
        "protected_value": ["What useful value the winning packet protects."],
        "bloat_or_pruning_risk": ["Any bloat, loss, or premature-pruning risk."],
        "composition_note": "How Step 6 should treat the packet privately.",
    }


@dataclasses.dataclass(frozen=True)
class _ValidationResult:
    value: dict[str, object]
    errors: list[str]


def _case_config(case_id: str) -> dict[str, object]:
    if case_id in CASE_CONFIGS:
        return CASE_CONFIGS[case_id]
    aliases = {
        _string(config.get("case_id")): key
        for key, config in CASE_CONFIGS.items()
        if _string(config.get("case_id"))
    }
    if case_id in aliases:
        return CASE_CONFIGS[aliases[case_id]]
    raise ContextCompositionValidationError(f"unknown fixed-suite case: {case_id}")


def _candidate_refs(config: dict[str, object]) -> dict[str, str]:
    refs = config.get("candidate_refs")
    if not isinstance(refs, dict):
        raise ContextCompositionValidationError("case config candidate_refs missing")
    required = ("rendered_hybrid", "bevelin_lens", "polya_lens")
    result = {field: str(refs.get(field, "")) for field in required}
    for field, ref in result.items():
        if not ref:
            raise ContextCompositionValidationError(f"missing candidate ref: {field}")
    return result


def _static_expectation(case_id: str) -> dict[str, list[str]]:
    if case_id not in STATIC_EXPECTATIONS:
        raise ContextCompositionValidationError(f"unknown fixed-suite case: {case_id}")
    expectation = STATIC_EXPECTATIONS[case_id]
    return {
        "allowed_winner_arms": list(expectation["allowed_winner_arms"]),
        "allowed_research_actions": list(expectation["allowed_research_actions"]),
    }


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise ContextCompositionValidationError(f"candidate artifact missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ContextCompositionValidationError(f"{path}: payload must be an object")
    return payload


def _answer_core(payload: dict[str, object]) -> str:
    answer = payload.get("answer_core")
    if not isinstance(answer, str) or not answer.strip():
        raise ContextCompositionValidationError("answer_core must be non-empty")
    return answer


def _candidate_refs_from_packet(packet: dict[str, object]) -> dict[str, str]:
    refs = packet.get("candidate_refs")
    if not isinstance(refs, dict):
        return {}
    return {str(key): str(value) for key, value in refs.items()}


def _blind_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(map_value) for key, map_value in value.items()}


def _validate_blind_map(value: object, path: Path) -> _ValidationResult:
    errors: list[str] = []
    if not isinstance(value, dict):
        return _ValidationResult({}, [f"{path}: blind_map must be an object"])
    result = {str(key): str(map_value) for key, map_value in value.items()}
    if set(result) != {"A", "B", "C", "D"}:
        errors.append(f"{path}: blind_map must contain labels A-D")
    if set(result.values()) != set(ARMS):
        errors.append(f"{path}: blind_map must contain the expected composition arms")
    return _ValidationResult(result, errors)


def _validate_reviewer_output(
    value: object,
    *,
    blind_map: _ValidationResult,
    path: Path,
) -> _ValidationResult:
    errors: list[str] = []
    if not isinstance(value, dict):
        return _ValidationResult({}, [f"{path}: reviewer_output must be an object"])
    errors.extend(_unknown_fields(value, REVIEWER_OUTPUT_FIELDS, path))
    errors.extend(_missing_fields(value, tuple(REVIEWER_OUTPUT_FIELDS), path))
    if errors:
        return _ValidationResult(dict(value), errors)

    winner_label = _string(value.get("winner_label"))
    if winner_label not in ALLOWED_LABELS:
        errors.append(f"{path / 'winner_label'}: unknown winner_label")
    elif winner_label != "tie" and winner_label not in blind_map.value:
        errors.append(f"{path / 'winner_label'}: winner_label not present in blind_map")
    if _string(value.get("research_action")) not in ALLOWED_ACTIONS:
        errors.append(f"{path / 'research_action'}: unknown research_action")
    if _string(value.get("confidence")) not in ALLOWED_CONFIDENCE:
        errors.append(f"{path / 'confidence'}: unknown confidence")
    for field in ("rationale", "composition_note"):
        if not _string(value.get(field)).strip():
            errors.append(f"{path / field}: must be non-empty")
    for field in ("protected_value", "bloat_or_pruning_risk"):
        if not _non_empty_string_list(value.get(field)):
            errors.append(f"{path / field}: must be a non-empty string list")
    return _ValidationResult(dict(value), errors)


def _validate_static_expectation(value: object, path: Path) -> _ValidationResult:
    errors: list[str] = []
    if not isinstance(value, dict):
        return _ValidationResult({}, [f"{path}: static_expectation must be an object"])
    errors.extend(_unknown_fields(value, STATIC_EXPECTATION_FIELDS, path))
    errors.extend(_missing_fields(value, tuple(STATIC_EXPECTATION_FIELDS), path))
    if errors:
        return _ValidationResult(dict(value), errors)
    winners = _string_list(value.get("allowed_winner_arms"))
    actions = _string_list(value.get("allowed_research_actions"))
    if not winners:
        errors.append(f"{path / 'allowed_winner_arms'}: must be non-empty")
    if not actions:
        errors.append(f"{path / 'allowed_research_actions'}: must be non-empty")
    for winner in winners:
        if winner not in set(ARMS) | {"tie"}:
            errors.append(f"{path / 'allowed_winner_arms'}: unknown arm {winner}")
    for action in actions:
        if action not in ALLOWED_ACTIONS:
            errors.append(f"{path / 'allowed_research_actions'}: unknown action {action}")
    return _ValidationResult(
        {
            "allowed_winner_arms": winners,
            "allowed_research_actions": actions,
        },
        errors,
    )


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


def _validate_candidate_refs(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: candidate_refs must be an object"
        return
    required = ("rendered_hybrid", "bevelin_lens", "polya_lens")
    yield from _missing_fields(value, required, path)
    for field in required:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    for field in sorted(set(value) - set(required)):
        yield f"{path / field}: unknown field"


def _score_agreement(
    *,
    reviewer_output: dict[str, object],
    blind_map: dict[str, str],
    static_expectation: dict[str, list[str]],
) -> dict[str, bool]:
    winner_label = _string(reviewer_output.get("winner_label"))
    winner_arm = "tie" if winner_label == "tie" else blind_map.get(winner_label, "")
    winner_matches = winner_arm in static_expectation.get("allowed_winner_arms", [])
    action_matches = _string(reviewer_output.get("research_action")) in (
        static_expectation.get("allowed_research_actions", [])
    )
    return {
        "winner_matches_static": winner_matches,
        "action_matches_static": action_matches,
        "overall_match": winner_matches and action_matches,
    }


def _validate_agreement(
    value: object,
    *,
    expected: dict[str, bool],
    path: Path,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: agreement must be an object"
        return
    yield from _unknown_fields(value, AGREEMENT_FIELDS, path)
    yield from _missing_fields(value, tuple(AGREEMENT_FIELDS), path)
    for field, expected_value in expected.items():
        if value.get(field) is not expected_value:
            yield f"{path / field}: must be {expected_value}"


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


def _normalize_reviewer_output(value: dict[str, object]) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    return {
        "winner_label": _string(value.get("winner_label")) or "tie",
        "research_action": _string(value.get("research_action")) or "retest",
        "confidence": _string(value.get("confidence")) or "low",
        "rationale": _string(value.get("rationale"))
        or "Reviewer returned no rationale.",
        "protected_value": _string_list(value.get("protected_value"))
        or ["Reviewer returned no protected value."],
        "bloat_or_pruning_risk": _string_list(value.get("bloat_or_pruning_risk"))
        or ["Reviewer returned no bloat or pruning risk."],
        "composition_note": _string(value.get("composition_note"))
        or "Reviewer returned no composition note.",
    }


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
        raise ContextCompositionValidationError(f"env file missing: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = " ".join(value.lower().split())
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(value)
    return result


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


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _non_empty_string_list(value: object) -> bool:
    return bool(_string_list(value))


def _parse_case_ids(args: argparse.Namespace) -> list[str]:
    if args.all:
        return list(STATIC_EXPECTATIONS)
    if args.case_id:
        return args.case_id
    raise ContextCompositionValidationError("provide --case-id or --all")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", default="")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            validate_composition_gate_judgment_file(path)
        return 0

    outputs: list[Path] = []
    for case_id in _parse_case_ids(args):
        output = run_live_gate(
            case_id=case_id,
            repo_root=args.repo_root,
            provider=args.provider,
            model=args.model,
            env_file=args.env_file,
            out_dir=args.out_dir,
            seed=args.seed,
            dry_run=args.dry_run,
        )
        if output is not None:
            outputs.append(output)
            print(output)
    if outputs:
        print(f"wrote {len(outputs)} context composition gate judgment(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
