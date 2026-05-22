#!/usr/bin/env python3
"""Research-only comparison of clean hybrid answers vs card-deck Step 6 replays."""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import random
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_cognitive_gate_live import CASE_CONFIGS
from pre_step6_raw_artifacts import validate_public_answer_hygiene


SCHEMA_VERSION = "pre_step6_card_deck_replay_comparison.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
COMPARISON_KIND = "clean_hybrid_vs_card_deck_replay"
JUDGMENT_SOURCE = "manual_llm_reviewer_judgment"
DEFAULT_OUT_DIR = Path("research/pre-step6-card-deck-replay-comparisons")
DEFAULT_SEED = 2026052003
ALLOWED_LABELS = frozenset({"A", "B", "tie"})
ALLOWED_ARMS = frozenset({"clean_hybrid", "card_deck_replay"})
ALLOWED_DECK_EFFECTS = frozenset({"improves", "equivalent", "regresses"})
ALLOWED_CONFIDENCE = frozenset({"high", "medium", "low"})
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "comparison_kind",
        "judgment_source",
        "provider_metadata",
        "candidate_refs",
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
        "deck_effect",
        "confidence",
        "rationale",
        "visible_improvements",
        "visible_regressions_or_bloat",
        "recommendation",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})


class ReplayComparisonValidationError(ValueError):
    pass


def build_replay_comparison_packet(
    *,
    case_id: str,
    repo_root: Path,
    seed: int = DEFAULT_SEED,
) -> dict[str, object]:
    refs = _candidate_refs(case_id)
    answers = {
        "clean_hybrid": _load_answer_core(repo_root / refs["clean_hybrid"]),
        "card_deck_replay": _load_replay_answer(repo_root / refs["card_deck_replay"]),
    }
    arms = list(answers)
    rng = random.Random(seed + sum(ord(char) for char in case_id))
    rng.shuffle(arms)
    labels = ("A", "B")
    blind_map = dict(zip(labels, arms, strict=True))
    candidates_by_label = {
        label: {
            "answer_core": answers[arm],
            "char_count": len(answers[arm]),
        }
        for label, arm in blind_map.items()
    }
    return {
        "case_id": case_id,
        "seed": seed,
        "comparison_kind": COMPARISON_KIND,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "reviewer_instruction": (
            "Compare the blinded answer cores as visible Step 6 outputs. Judge "
            "which candidate is better without rewarding bloat, private machinery "
            "leakage, or mere paraphrase. Do not solve the underlying case again."
        ),
        "candidates_by_label": candidates_by_label,
        "candidate_refs": refs,
        "blind_map": blind_map,
        "response_schema": _response_schema(),
    }


def build_reviewer_packet(packet: dict[str, object]) -> dict[str, object]:
    allowed = {
        "case_id",
        "status",
        "runtime_policy",
        "reviewer_instruction",
        "candidates_by_label",
        "response_schema",
    }
    return {key: value for key, value in packet.items() if key in allowed}


def build_replay_comparison_payload(
    *,
    packet: dict[str, object],
    reviewer_output: dict[str, object],
    provider_metadata: dict[str, object],
    notes: str = "",
) -> dict[str, object]:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "case_id": _string(packet.get("case_id")),
        "comparison_kind": COMPARISON_KIND,
        "judgment_source": JUDGMENT_SOURCE,
        "provider_metadata": provider_metadata,
        "candidate_refs": _string_dict(packet.get("candidate_refs")),
        "blind_map": _string_dict(packet.get("blind_map")),
        "reviewer_output": _normalize_reviewer_output(
            reviewer_output,
            blind_map=_string_dict(packet.get("blind_map")),
        ),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": notes,
    }
    validate_replay_comparison_payload(payload)
    return payload


def load_replay_comparison_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReplayComparisonValidationError(f"{path}: payload must be an object")
    return payload


def validate_replay_comparison_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_replay_comparison_errors(payload, path=Path(path)))
    if errors:
        raise ReplayComparisonValidationError("; ".join(errors))


def validate_replay_comparison_file(path: Path) -> None:
    validate_replay_comparison_payload(load_replay_comparison_payload(path), path=Path(path))


def iter_replay_comparison_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(TOP_LEVEL_FIELDS - {"notes"})
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
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    if _string(payload.get("comparison_kind")) != COMPARISON_KIND:
        yield f"{path / 'comparison_kind'}: must be {COMPARISON_KIND}"
    if _string(payload.get("judgment_source")) != JUDGMENT_SOURCE:
        yield f"{path / 'judgment_source'}: must be {JUDGMENT_SOURCE}"

    yield from _validate_provider_metadata(
        payload.get("provider_metadata"),
        path / "provider_metadata",
    )
    yield from _validate_candidate_refs(payload.get("candidate_refs"), path / "candidate_refs")
    blind_map = _validate_blind_map(payload.get("blind_map"), path / "blind_map")
    yield from blind_map.errors
    yield from _validate_reviewer_output(
        payload.get("reviewer_output"),
        blind_map=blind_map.value,
        path=path / "reviewer_output",
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def run_live_comparison(
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
    packet = build_replay_comparison_packet(
        case_id=case_id,
        repo_root=repo_root,
        seed=seed,
    )
    reviewer_packet = build_reviewer_packet(packet)
    if dry_run:
        print(json.dumps(reviewer_packet, indent=2, ensure_ascii=False))
        return None

    sys.path.insert(0, str(repo_root / "engine"))
    sys.path.insert(0, str(repo_root))
    from system_b.boundary_provider import load_boundary_client_from_env  # noqa: PLC0415

    client = load_boundary_client_from_env(provider)
    output, metadata = client.run_json_with_metadata(
        _system_prompt(),
        json.dumps(reviewer_packet, indent=2, ensure_ascii=False),
        stage="pre_step6_card_deck_replay_comparison",
        tendency_id=case_id,
    )
    provider_metadata = _provider_metadata_dict(metadata)
    if _string(provider_metadata.get("status")) != "ok":
        raise ReplayComparisonValidationError(
            "live replay comparison failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    payload = build_replay_comparison_payload(
        packet=packet,
        reviewer_output=output,
        provider_metadata=provider_metadata,
        notes="Live research comparison of clean hybrid vs card-deck Step 6 replay.",
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{case_id}.card-deck-replay-comparison.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    validate_replay_comparison_file(out_path)
    return out_path


def _candidate_refs(case_id: str) -> dict[str, str]:
    config = CASE_CONFIGS.get(case_id)
    if config is None:
        raise ReplayComparisonValidationError(f"unknown fixed-suite case: {case_id}")
    refs = config.get("candidate_refs")
    if not isinstance(refs, dict):
        raise ReplayComparisonValidationError("case config candidate_refs missing")
    rendered = str(refs.get("rendered_hybrid", ""))
    if not rendered:
        raise ReplayComparisonValidationError("rendered_hybrid ref missing")
    return {
        "clean_hybrid": rendered,
        "card_deck_replay": (
            f"research/pre-step6-card-deck-replays/{case_id}.card-deck-replay.v1.json"
        ),
    }


def _load_answer_core(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReplayComparisonValidationError(f"{path}: payload must be object")
    answer = payload.get("answer_core")
    if not isinstance(answer, str) or not answer.strip():
        raise ReplayComparisonValidationError(f"{path}: answer_core missing")
    validate_public_answer_hygiene(answer)
    return answer


def _load_replay_answer(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReplayComparisonValidationError(f"{path}: payload must be object")
    output = payload.get("step6_output")
    if not isinstance(output, dict):
        raise ReplayComparisonValidationError(f"{path}: step6_output missing")
    answer = output.get("answer_core")
    if not isinstance(answer, str) or not answer.strip():
        raise ReplayComparisonValidationError(f"{path}: answer_core missing")
    validate_public_answer_hygiene(answer)
    return answer


def _response_schema() -> dict[str, object]:
    return {
        "winner_label": "A | B | tie",
        "confidence": "high | medium | low",
        "rationale": "Short comparison rationale.",
        "visible_improvements": ["What got better, if anything."],
        "visible_regressions_or_bloat": ["What got worse or bloated, if anything."],
        "recommendation": "What to do next with the tested candidate path.",
    }


def _system_prompt() -> str:
    return (
        "You are a research reviewer comparing two blinded Step 6 answer cores. "
        "Do not solve the underlying case. Judge visible answer quality: concrete "
        "decision usefulness, preservation of nuance, absence of bloat, and absence "
        "of private machinery leakage. Keep your output internally consistent: "
        "winner_label is the answer you judge best, and tie means neither answer is "
        "meaningfully better. Return strict JSON only."
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
    required = ("clean_hybrid", "card_deck_replay")
    yield from _missing_fields(value, required, path)
    for field in required:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    for field in sorted(set(value) - set(required)):
        yield f"{path / field}: unknown field"


class _BlindMapResult:
    def __init__(self, value: dict[str, str], errors: list[str]) -> None:
        self.value = value
        self.errors = errors


def _validate_blind_map(value: object, path: Path) -> _BlindMapResult:
    errors: list[str] = []
    if not isinstance(value, dict):
        return _BlindMapResult({}, [f"{path}: blind_map must be an object"])
    result = {str(key): str(map_value) for key, map_value in value.items()}
    if set(result) != {"A", "B"}:
        errors.append(f"{path}: blind_map must contain A and B")
    if set(result.values()) != ALLOWED_ARMS:
        errors.append(f"{path}: blind_map must contain clean_hybrid and card_deck_replay")
    return _BlindMapResult(result, errors)


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
    winner = _string(value.get("winner_label"))
    if winner not in ALLOWED_LABELS:
        yield f"{path / 'winner_label'}: unknown winner_label"
    elif winner != "tie" and winner not in blind_map:
        yield f"{path / 'winner_label'}: winner_label not in blind_map"
    if _string(value.get("deck_effect")) not in ALLOWED_DECK_EFFECTS:
        yield f"{path / 'deck_effect'}: unknown deck_effect"
    else:
        yield from _validate_winner_effect_consistency(
            winner=winner,
            deck_effect=_string(value.get("deck_effect")),
            blind_map=blind_map,
            path=path / "deck_effect",
        )
    if _string(value.get("confidence")) not in ALLOWED_CONFIDENCE:
        yield f"{path / 'confidence'}: unknown confidence"
    for field in ("rationale", "recommendation"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    for field in ("visible_improvements", "visible_regressions_or_bloat"):
        if not _string_list(value.get(field)):
            yield f"{path / field}: must be a non-empty string list"


def _validate_winner_effect_consistency(
    *,
    winner: str,
    deck_effect: str,
    blind_map: dict[str, str],
    path: Path,
) -> Iterable[str]:
    deck_label = next(
        (label for label, arm in blind_map.items() if arm == "card_deck_replay"),
        "",
    )
    clean_label = next(
        (label for label, arm in blind_map.items() if arm == "clean_hybrid"),
        "",
    )
    if deck_effect == "improves" and winner == clean_label:
        yield f"{path}: cannot be improves when clean_hybrid is the winner"
    if deck_effect == "regresses" and winner == deck_label:
        yield f"{path}: cannot be regresses when card_deck_replay is the winner"
    if winner == "tie" and deck_effect != "equivalent":
        yield f"{path}: tie winner requires equivalent deck_effect"


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


def _normalize_reviewer_output(
    value: dict[str, object],
    *,
    blind_map: dict[str, str],
) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    winner = _string(value.get("winner_label")) or "tie"
    return {
        "winner_label": winner,
        "deck_effect": _compute_deck_effect(winner, blind_map),
        "confidence": _string(value.get("confidence")) or "low",
        "rationale": _string(value.get("rationale")) or "Reviewer returned no rationale.",
        "visible_improvements": _string_list(value.get("visible_improvements"))
        or ["Reviewer returned no visible improvements."],
        "visible_regressions_or_bloat": _string_list(
            value.get("visible_regressions_or_bloat")
        )
        or ["Reviewer returned no regressions or bloat."],
        "recommendation": _string(value.get("recommendation"))
        or "Reviewer returned no recommendation.",
    }


def _compute_deck_effect(winner: str, blind_map: dict[str, str]) -> str:
    if winner == "tie":
        return "equivalent"
    if blind_map.get(winner) == "card_deck_replay":
        return "improves"
    if blind_map.get(winner) == "clean_hybrid":
        return "regresses"
    return "equivalent"


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
        raise ReplayComparisonValidationError(f"env file missing: {path}")
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


def _string_dict(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(map_value) for key, map_value in value.items()}


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _parse_case_ids(args: argparse.Namespace) -> list[str]:
    if args.all:
        return [
            "founder-grant-marcus-equity.high-clutter",
            "third-year-phd-student.v2",
            "mid-level-consultant-report-2",
            "mother-address-year",
        ]
    if args.case_id:
        return args.case_id
    raise ReplayComparisonValidationError("provide --case-id or --all")


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
            validate_replay_comparison_file(path)
        return 0

    outputs: list[Path] = []
    for case_id in _parse_case_ids(args):
        output = run_live_comparison(
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
        print(f"wrote {len(outputs)} replay comparison(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
