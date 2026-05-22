#!/usr/bin/env python3
"""Research-only live cognitive comparison gate for pre-Step-6 candidates.

The gate asks a small reviewer call to compare already-generated candidate
answer cores. It does not select runtime behavior, edit SKILL.md, or promote a
candidate into product docs.
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


SCHEMA_VERSION = "pre_step6_cognitive_gate_judgment.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
GATE_KIND = "live_small_cognitive_comparison"
JUDGMENT_SOURCE = "manual_llm_reviewer_judgment"
DEFAULT_OUT_DIR = Path("research/pre-step6-cognitive-gate-judgments")
DEFAULT_SEED = 2026052001
ALLOWED_LABELS = frozenset({"A", "B", "C", "D", "tie"})
ALLOWED_ARMS = frozenset(
    {"rendered_hybrid", "portfolio_base", "bevelin_lens", "polya_lens", "tie"}
)
ALLOWED_PROMOTION_READS = frozenset({"expand_replay", "retest", "stop"})
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
REVIEWER_OUTPUT_FIELDS = frozenset(
    {
        "winner_label",
        "promotion_read",
        "confidence",
        "rationale",
        "improvements",
        "regressions_or_watch_items",
        "stand_down_reason",
        "composition_note",
    }
)
STATIC_EXPECTATION_FIELDS = frozenset(
    {"allowed_winner_arms", "allowed_promotion_reads"}
)
AGREEMENT_FIELDS = frozenset(
    {"winner_matches_static", "promotion_matches_static", "overall_match"}
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
RUBRIC = (
    {
        "criterion_id": "decision_usefulness",
        "question": (
            "Which candidate most improves the advice Step 6 would give, "
            "without drifting into an unrelated essay?"
        ),
    },
    {
        "criterion_id": "source_grounding",
        "question": (
            "Which candidate most clearly uses only the case evidence and avoids "
            "inventing facts?"
        ),
    },
    {
        "criterion_id": "overclaim_risk",
        "question": (
            "Which candidate keeps uncertainty visible instead of converting "
            "thin evidence into confident claims?"
        ),
    },
    {
        "criterion_id": "answer_length_cognitive_load",
        "question": (
            "Which candidate gives Step 6 enough breadth without creating avoidable "
            "reading load?"
        ),
    },
    {
        "criterion_id": "machinery_hygiene",
        "question": (
            "Which candidate keeps private machinery invisible in the user-facing "
            "answer shape?"
        ),
    },
    {
        "criterion_id": "conflict_preservation",
        "question": (
            "Which candidate best preserves the real conflict or tension that Step 6 "
            "must reason through?"
        ),
    },
    {
        "criterion_id": "edge_pressure_preservation",
        "question": (
            "Which candidate best preserves non-obvious pressure that may matter even "
            "if it is not the obvious narrative?"
        ),
    },
    {
        "criterion_id": "breadth_depth_preservation",
        "question": (
            "Which candidate best keeps enough breadth and depth so Step 6 can think "
            "out of the box?"
        ),
    },
    {
        "criterion_id": "premature_pruning_risk",
        "question": (
            "Which candidate least risks castrating the search space before Step 6 has "
            "done the real thinking?"
        ),
    },
    {
        "criterion_id": "negative_control_discipline",
        "question": (
            "Which candidate knows when to stand down because the existing answer is "
            "already good enough?"
        ),
    },
)


class CognitiveGateValidationError(ValueError):
    pass


CASE_CONFIGS: dict[str, dict[str, object]] = {
    "founder-grant-marcus-equity.high-clutter": {
        "artifact_slug": "founder-grant-marcus-equity.high-clutter",
        "candidate_refs": {
            "rendered_hybrid": (
                "research/pre-step6-rendered-hybrid-answer-cores/"
                "founder-grant-marcus-equity.high-clutter.native.rendered-hybrid-answer-core.v1.json"
            ),
            "portfolio_base": (
                "research/pre-step6-portfolio-answer-cores/"
                "founder-grant-marcus-equity.high-clutter.native.portfolio-answer-core.v1.json"
            ),
            "bevelin_lens": (
                "research/pre-step6-lens-answer-cores/"
                "founder-grant-marcus-equity.high-clutter.bevelin-answer-core.v1.json"
            ),
            "polya_lens": (
                "research/pre-step6-lens-answer-cores/"
                "founder-grant-marcus-equity.high-clutter.polya-answer-core.v1.json"
            ),
        },
        "static_expectation": {
            "allowed_winner_arms": ["bevelin_lens"],
            "allowed_promotion_reads": ["expand_replay"],
        },
        "case_note": (
            "Founder equity case with high artifact clutter. The suspected value of "
            "the lens layer is protected incentive and dependency pressure."
        ),
    },
    "third-year-phd-student.v2": {
        "case_id": "third-year-phd-student",
        "artifact_slug": "third-year-phd-student.v2",
        "candidate_refs": {
            "rendered_hybrid": (
                "research/pre-step6-rendered-hybrid-answer-cores/"
                "third-year-phd-student.conflict.native.rendered-hybrid-answer-core.v1.json"
            ),
            "portfolio_base": (
                "research/pre-step6-portfolio-answer-cores/"
                "third-year-phd-student.v2.native.portfolio-answer-core.v1.json"
            ),
            "bevelin_lens": (
                "research/pre-step6-lens-answer-cores/"
                "third-year-phd-student.v2.bevelin-answer-core.v1.json"
            ),
            "polya_lens": (
                "research/pre-step6-lens-answer-cores/"
                "third-year-phd-student.v2.polya-answer-core.v1.json"
            ),
        },
        "static_expectation": {
            "allowed_winner_arms": ["bevelin_lens", "polya_lens"],
            "allowed_promotion_reads": ["expand_replay"],
        },
        "case_note": (
            "PhD advisor conflict case. The suspected value of the lens layer is "
            "clearer problem shape, commitment pressure, and next-move sequencing."
        ),
    },
    "mid-level-consultant-report-2": {
        "artifact_slug": "mid-level-consultant-report-2",
        "candidate_refs": {
            "rendered_hybrid": (
                "research/pre-step6-rendered-hybrid-answer-cores/"
                "mid-level-consultant-report-2.native.rendered-hybrid-answer-core.v1.json"
            ),
            "portfolio_base": (
                "research/pre-step6-portfolio-answer-cores/"
                "mid-level-consultant-report-2.native.portfolio-answer-core.v1.json"
            ),
            "bevelin_lens": (
                "research/pre-step6-lens-answer-cores/"
                "mid-level-consultant-report-2.bevelin-answer-core.v1.json"
            ),
            "polya_lens": (
                "research/pre-step6-lens-answer-cores/"
                "mid-level-consultant-report-2.polya-answer-core.v1.json"
            ),
        },
        "static_expectation": {
            "allowed_winner_arms": ["rendered_hybrid"],
            "allowed_promotion_reads": ["stop"],
        },
        "case_note": (
            "Consultant negative-control case. The suspected best behavior is "
            "stand-down because rendered hybrid already preserves counsel-first sequencing."
        ),
    },
    "mother-address-year": {
        "artifact_slug": "mother-address-year",
        "candidate_refs": {
            "rendered_hybrid": (
                "research/pre-step6-rendered-hybrid-answer-cores/"
                "mother-address-year.native.rendered-hybrid-answer-core.v1.json"
            ),
            "portfolio_base": (
                "research/pre-step6-portfolio-answer-cores/"
                "mother-address-year.native.portfolio-answer-core.v1.json"
            ),
            "bevelin_lens": (
                "research/pre-step6-lens-answer-cores/"
                "mother-address-year.bevelin-answer-core.v1.json"
            ),
            "polya_lens": (
                "research/pre-step6-lens-answer-cores/"
                "mother-address-year.polya-answer-core.v1.json"
            ),
        },
        "static_expectation": {
            "allowed_winner_arms": [
                "portfolio_base",
                "bevelin_lens",
                "polya_lens",
                "tie",
            ],
            "allowed_promotion_reads": ["retest"],
        },
        "case_note": (
            "Mother address-year quiet case. The suspected best behavior is useful "
            "uncertainty enrichment without over-promoting."
        ),
    },
}


def build_gate_packet(
    *,
    case_id: str,
    repo_root: Path,
    seed: int = DEFAULT_SEED,
) -> dict[str, object]:
    """Build a blinded comparison packet and private map for later scoring."""
    config = _case_config(case_id)
    refs = _candidate_refs(config)
    arms = list(refs)
    rng = random.Random(seed + sum(ord(char) for char in case_id))
    rng.shuffle(arms)
    labels = ("A", "B", "C", "D")
    blind_map = dict(zip(labels, arms, strict=True))
    candidates_by_label: dict[str, dict[str, object]] = {}
    for label, arm in blind_map.items():
        answer_core = _load_answer_core(repo_root / refs[arm])
        candidates_by_label[label] = {
            "answer_core": answer_core,
            "char_count": len(answer_core),
        }
    return {
        "case_id": case_id,
        "seed": seed,
        "gate_kind": GATE_KIND,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "reviewer_instruction": _reviewer_instruction(),
        "case_note": _string(config.get("case_note")),
        "rubric": list(RUBRIC),
        "candidates_by_label": candidates_by_label,
        "candidate_refs": refs,
        "blind_map": blind_map,
        "response_schema": _response_schema(),
        "policy": {
            "do_not_write_a_final_answer": True,
            "compare_context_quality_only": True,
            "prefer_enrichment_over_premature_pruning": True,
            "stand_down_when_candidate_adds_bloat_without_new_quality": True,
        },
    }


def build_reviewer_packet(packet: dict[str, object]) -> dict[str, object]:
    """Return the packet subset that can be sent to a blinded reviewer."""
    allowed = {
        "case_id",
        "gate_kind",
        "status",
        "runtime_policy",
        "reviewer_instruction",
        "case_note",
        "rubric",
        "candidates_by_label",
        "response_schema",
        "policy",
    }
    return {key: value for key, value in packet.items() if key in allowed}


def build_gate_judgment_payload(
    *,
    packet: dict[str, object],
    reviewer_output: dict[str, object],
    provider_metadata: dict[str, object],
    notes: str = "",
) -> dict[str, object]:
    config = _case_config(_string(packet.get("case_id")))
    static_expectation = _static_expectation(config)
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
    validate_gate_judgment_payload(payload)
    return payload


def load_gate_judgment_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CognitiveGateValidationError(f"{path}: payload must be an object")
    return payload


def validate_gate_judgment_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_gate_judgment_errors(payload, path=Path(path)))
    if errors:
        raise CognitiveGateValidationError("; ".join(errors))


def validate_gate_judgment_file(path: Path) -> None:
    validate_gate_judgment_payload(load_gate_judgment_payload(path), path=Path(path))


def iter_gate_judgment_errors(
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
    case_id = _string(payload.get("case_id"))
    if case_id not in CASE_CONFIGS:
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

    packet = build_gate_packet(case_id=case_id, repo_root=repo_root, seed=seed)
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
        stage="pre_step6_cognitive_gate",
        tendency_id=case_id,
    )
    metadata_dict = _provider_metadata_dict(metadata)
    if _string(metadata_dict.get("status")) != "ok":
        raise CognitiveGateValidationError(
            "live reviewer call failed with status "
            f"{_string(metadata_dict.get('status')) or 'unknown'}"
        )
    if not reviewer_output:
        raise CognitiveGateValidationError("live reviewer returned an empty payload")
    reviewer_output = _normalize_reviewer_output(reviewer_output)
    payload = build_gate_judgment_payload(
        packet=packet,
        reviewer_output=reviewer_output,
        provider_metadata=metadata_dict,
        notes=(
            "Live small cognitive comparison. Research-only artifact; it records "
            "reviewer agreement or disagreement with static expectations."
        ),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_slug = _string(_case_config(case_id).get("artifact_slug")) or case_id
    out_path = out_dir / f"{artifact_slug}.live-cognitive-gate.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    validate_gate_judgment_file(out_path)
    return out_path


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
    raise CognitiveGateValidationError(f"unknown fixed-suite case: {case_id}")


def _candidate_refs(config: dict[str, object]) -> dict[str, str]:
    refs = config.get("candidate_refs")
    if not isinstance(refs, dict):
        raise CognitiveGateValidationError("case config candidate_refs must be an object")
    result = {str(key): str(value) for key, value in refs.items()}
    if set(result) != {"rendered_hybrid", "portfolio_base", "bevelin_lens", "polya_lens"}:
        raise CognitiveGateValidationError("case config candidate refs have wrong arms")
    return result


def _static_expectation(config: dict[str, object]) -> dict[str, list[str]]:
    value = config.get("static_expectation")
    if not isinstance(value, dict):
        raise CognitiveGateValidationError("case config expectation must be an object")
    return {
        "allowed_winner_arms": _string_list(value.get("allowed_winner_arms")),
        "allowed_promotion_reads": _string_list(value.get("allowed_promotion_reads")),
    }


def _candidate_refs_from_packet(packet: dict[str, object]) -> dict[str, str]:
    refs = packet.get("candidate_refs")
    if not isinstance(refs, dict):
        return {}
    return {str(key): str(value) for key, value in refs.items()}


def _blind_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(map_value) for key, map_value in value.items()}


def _load_answer_core(path: Path) -> str:
    if not path.exists():
        raise CognitiveGateValidationError(f"candidate answer core missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CognitiveGateValidationError(f"{path}: payload must be an object")
    answer_core = payload.get("answer_core")
    if not isinstance(answer_core, str) or not answer_core.strip():
        raise CognitiveGateValidationError(f"{path}: answer_core must be non-empty")
    return answer_core


def _reviewer_instruction() -> str:
    return (
        "Compare the blinded candidate answer cores as inputs to a later Step 6 "
        "reasoning answer. Do not write the final user answer. Do not judge which "
        "candidate is the best final answer, prose template, or response draft. "
        "Judge which candidate would give Step 6 the strongest private cognitive "
        "input: useful edge pressure, problem shape, breadth, or depth without "
        "premature pruning. Prefer enrichment over neatness when the enrichment "
        "helps reasoning, but stand down when a candidate only adds bloat or "
        "flattens the case. promotion_read applies to the research layer: "
        "expand_replay means the added portfolio/lens machinery deserves more "
        "replay testing; retest means useful but not decisive; stop means the "
        "extra layer should stand down for this case. Return only JSON matching "
        "response_schema."
    )


def _system_prompt() -> str:
    return (
        "You are a cognitive comparison gate for a research-only pre-Step-6 "
        "context experiment. Your job is not deterministic selection and not final "
        "answer generation. Do not judge which candidate is the best final answer "
        "or writing template. Use judgment: compare the blinded candidate answer "
        "cores, pick the candidate that would most improve Step 6's private "
        "cognitive input, or tie if the right result is no clear winner. Separately "
        "set promotion_read for the research layer, not for the winning prose: "
        "expand_replay only when the extra pre-Step-6 machinery deserves more "
        "testing; retest for useful but indecisive; stop when the existing baseline "
        "should stand. You must preserve breadth and edge pressure; do not punish "
        "useful non-obvious material just because it is not the main narrative. "
        "Also do not reward bloat. Return strict JSON only."
    )


def _response_schema() -> dict[str, object]:
    return {
        "winner_label": "A | B | C | D | tie",
        "promotion_read": (
            "expand_replay | retest | stop. This applies to the research layer, "
            "not to whether the winning prose is a good final answer."
        ),
        "confidence": "high | medium | low",
        "rationale": "Short explanation of the quality judgment.",
        "improvements": ["Concrete ways the winner improves Step 6 context."],
        "regressions_or_watch_items": ["Concrete risks or lost value."],
        "stand_down_reason": "If promotion_read is stop, explain why. Otherwise say why this is not a stand-down.",
        "composition_note": "How to compose or not compose this candidate with the others.",
    }


@dataclasses.dataclass(frozen=True)
class _ValidationResult:
    value: dict[str, object]
    errors: list[str]


def _validate_blind_map(value: object, path: Path) -> _ValidationResult:
    errors: list[str] = []
    if not isinstance(value, dict):
        return _ValidationResult({}, [f"{path}: blind_map must be an object"])
    result = {str(key): str(map_value) for key, map_value in value.items()}
    if set(result) != {"A", "B", "C", "D"}:
        errors.append(f"{path}: blind_map must contain labels A-D")
    if set(result.values()) != {
        "rendered_hybrid",
        "portfolio_base",
        "bevelin_lens",
        "polya_lens",
    }:
        errors.append(f"{path}: blind_map must contain the four expected arms")
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
    yield_errors = list(_unknown_fields(value, REVIEWER_OUTPUT_FIELDS, path))
    yield_errors.extend(_missing_fields(value, tuple(REVIEWER_OUTPUT_FIELDS), path))
    errors.extend(yield_errors)
    if yield_errors:
        return _ValidationResult(dict(value), errors)

    winner_label = _string(value.get("winner_label"))
    if winner_label not in ALLOWED_LABELS:
        errors.append(f"{path / 'winner_label'}: unknown winner_label")
    elif winner_label != "tie" and winner_label not in blind_map.value:
        errors.append(f"{path / 'winner_label'}: winner_label not present in blind_map")
    if _string(value.get("promotion_read")) not in ALLOWED_PROMOTION_READS:
        errors.append(f"{path / 'promotion_read'}: unknown promotion_read")
    if _string(value.get("confidence")) not in ALLOWED_CONFIDENCE:
        errors.append(f"{path / 'confidence'}: unknown confidence")
    for field in ("rationale", "stand_down_reason", "composition_note"):
        if not _string(value.get(field)).strip():
            errors.append(f"{path / field}: must be non-empty")
    for field in ("improvements", "regressions_or_watch_items"):
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
    promotion_reads = _string_list(value.get("allowed_promotion_reads"))
    if not winners:
        errors.append(f"{path / 'allowed_winner_arms'}: must be non-empty")
    if not promotion_reads:
        errors.append(f"{path / 'allowed_promotion_reads'}: must be non-empty")
    for winner in winners:
        if winner not in ALLOWED_ARMS:
            errors.append(f"{path / 'allowed_winner_arms'}: unknown arm {winner}")
    for promotion_read in promotion_reads:
        if promotion_read not in ALLOWED_PROMOTION_READS:
            errors.append(
                f"{path / 'allowed_promotion_reads'}: unknown read {promotion_read}"
            )
    return _ValidationResult(
        {
            "allowed_winner_arms": winners,
            "allowed_promotion_reads": promotion_reads,
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
    unknown = sorted(set(value) - PROVIDER_METADATA_FIELDS)
    for field in unknown:
        yield f"{path / field}: unknown field"


def _validate_candidate_refs(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: candidate_refs must be an object"
        return
    required = ("rendered_hybrid", "portfolio_base", "bevelin_lens", "polya_lens")
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
    if winner_label == "tie":
        winner_arm = "tie"
    else:
        winner_arm = blind_map.get(winner_label, "")
    winner_matches = winner_arm in static_expectation.get("allowed_winner_arms", [])
    promotion_matches = _string(reviewer_output.get("promotion_read")) in (
        static_expectation.get("allowed_promotion_reads", [])
    )
    return {
        "winner_matches_static": winner_matches,
        "promotion_matches_static": promotion_matches,
        "overall_match": winner_matches and promotion_matches,
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
        "promotion_read": _string(value.get("promotion_read")) or "retest",
        "confidence": _string(value.get("confidence")) or "low",
        "rationale": _string(value.get("rationale"))
        or "Reviewer returned no rationale.",
        "improvements": _string_list(value.get("improvements"))
        or ["Reviewer returned no improvements."],
        "regressions_or_watch_items": _string_list(
            value.get("regressions_or_watch_items")
        )
        or ["Reviewer returned no regressions or watch items."],
        "stand_down_reason": _string(value.get("stand_down_reason"))
        or "Reviewer returned no stand-down reason.",
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
        raise CognitiveGateValidationError(f"env file missing: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


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
        return list(CASE_CONFIGS)
    if args.case_id:
        return args.case_id
    raise CognitiveGateValidationError("provide --case-id or --all")


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
            validate_gate_judgment_file(path)
        return 0

    outputs: list[Path] = []
    for case_id in _parse_case_ids(args):
        out_path = run_live_gate(
            case_id=case_id,
            repo_root=args.repo_root,
            provider=args.provider,
            model=args.model,
            env_file=args.env_file,
            out_dir=args.out_dir,
            seed=args.seed,
            dry_run=args.dry_run,
        )
        if out_path is not None:
            outputs.append(out_path)
            print(out_path)
    if outputs:
        print(f"wrote {len(outputs)} cognitive gate judgment(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
