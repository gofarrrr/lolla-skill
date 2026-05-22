#!/usr/bin/env python3
"""Research-only cost/cache contract for the Step 6 private card deck.

This does not generate cards or change runtime behavior. It records the
cache-key material and mode-specific cold-path policy needed before any cached
cards first integration draft.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_step6_card_deck import build_step6_card_deck, validate_step6_card_deck_payload


SCHEMA_VERSION = "pre_step6_design_preamble_cost_cache.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "design_preamble_cost_cache_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-design-preamble-cost-cache")
DECK_BUILDER_VERSION = "pre_step6_step6_card_deck.v1"
STEP6_PROMPT_CONTRACT_VERSION = "pre_step6_card_deck_replay_prompt.v1"
ALLOWED_CACHE_MODES = frozenset(
    {"off", "research", "experimental", "runtime_cached_only"}
)
REQUIRED_KEY_MATERIAL_FIELDS = frozenset(
    {
        "card_deck_schema_version",
        "deck_builder_version",
        "lens_pack_versions",
        "lens_substrate_hashes",
        "conversation_ir_hash",
        "problem_state_hash",
        "rendered_hybrid_anchor_hash",
        "v60_selected_item_hashes",
        "safety_profile_flags",
        "step6_prompt_contract_version",
    }
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "case_id",
        "source_refs",
        "key_material",
        "compiled_card_deck_key",
        "cache_read",
        "cost_envelope",
        "runtime_effect",
        "gates",
        "notes",
    }
)
CACHE_READ_FIELDS = frozenset(
    {"cache_mode", "cache_hit", "miss_behavior", "cold_path_policy"}
)
COST_ENVELOPE_FIELDS = frozenset(
    {
        "net_new_llm_calls",
        "live_card_generation_allowed",
        "normal_runtime_reviewer_calls",
        "token_cost_read",
    }
)
RUNTIME_EFFECT_FIELDS = frozenset(
    {"step6_card_deck_presented", "records_issue", "fallback_behavior"}
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})


class CostCacheContractValidationError(ValueError):
    pass


def build_cost_cache_contract(
    *,
    case_id: str,
    repo_root: Path,
    cache_mode: str = "runtime_cached_only",
    cache_hit: bool = False,
    v60_selected_item_hashes: Sequence[str] = (),
) -> dict[str, object]:
    if cache_mode not in ALLOWED_CACHE_MODES:
        raise CostCacheContractValidationError(f"unsupported cache mode: {cache_mode}")

    card_deck = build_step6_card_deck(case_id=case_id, repo_root=repo_root)
    validate_step6_card_deck_payload(card_deck)
    source_refs = dict(card_deck["source_refs"])
    key_material = _key_material(
        case_id=case_id,
        repo_root=repo_root,
        source_refs=source_refs,
        v60_selected_item_hashes=v60_selected_item_hashes,
    )
    cache_read = _cache_read(cache_mode=cache_mode, cache_hit=cache_hit)
    cost_envelope = _cost_envelope(cache_mode=cache_mode, cache_hit=cache_hit)
    runtime_effect = _runtime_effect(
        cache_mode=cache_mode,
        cache_hit=cache_hit,
        miss_behavior=str(cache_read["miss_behavior"]),
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case_id,
        "source_refs": source_refs,
        "key_material": key_material,
        "compiled_card_deck_key": _compiled_key(key_material),
        "cache_read": cache_read,
        "cost_envelope": cost_envelope,
        "runtime_effect": runtime_effect,
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only cost/cache contract. Normal runtime cached-only mode "
            "does not cold-generate cards; a miss stands down to current Step 6 "
            "and records an audit issue."
        ),
    }
    validate_cost_cache_contract_payload(payload)
    return payload


def load_cost_cache_contract_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CostCacheContractValidationError(f"{path}: payload must be an object")
    return payload


def validate_cost_cache_contract_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_cost_cache_contract_errors(payload, path=Path(path)))
    if errors:
        raise CostCacheContractValidationError("; ".join(errors))


def validate_cost_cache_contract_file(path: Path) -> None:
    validate_cost_cache_contract_payload(
        load_cost_cache_contract_payload(path),
        path=Path(path),
    )


def iter_cost_cache_contract_errors(
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
    if _string(payload.get("experiment_id")) != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    yield from _validate_key_material(payload.get("key_material"), path / "key_material")
    yield from _validate_compiled_key(payload, path)
    yield from _validate_cache_read(payload.get("cache_read"), path / "cache_read")
    yield from _validate_cost_envelope(
        payload.get("cost_envelope"),
        path / "cost_envelope",
    )
    yield from _validate_runtime_effect(
        payload.get("runtime_effect"),
        path / "runtime_effect",
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")
    yield from _validate_runtime_cached_only_policy(payload, path)


def write_cost_cache_contract(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_cost_cache_contract_payload(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    mode = _string(payload["cache_read"]["cache_mode"])  # type: ignore[index]
    hit = "hit" if payload["cache_read"]["cache_hit"] is True else "miss"  # type: ignore[index]
    out_path = out_dir / f"{_string(payload['case_id'])}.{mode}.{hit}.cost-cache.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_path


def _key_material(
    *,
    case_id: str,
    repo_root: Path,
    source_refs: dict[str, object],
    v60_selected_item_hashes: Sequence[str],
) -> dict[str, object]:
    rendered_ref = _string(source_refs.get("rendered_hybrid"))
    bevelin_ref = _string(source_refs.get("bevelin_lens"))
    polya_ref = _string(source_refs.get("polya_lens"))
    problem_state_ref = _string(source_refs.get("problem_state"))
    return {
        "card_deck_schema_version": "pre_step6_card_deck.v1",
        "deck_builder_version": DECK_BUILDER_VERSION,
        "lens_pack_versions": {
            "bevelin": "bevelin_seeking_wisdom_v0",
            "polya": "polya_problem_solving_v0",
        },
        "lens_substrate_hashes": {
            "bevelin": {
                "hash": _hash_file(repo_root / bevelin_ref),
                "source_ref": bevelin_ref,
                "research_proxy": True,
                "note": "Current research slice hashes the lens answer-core artifact as a proxy for future cached lens substrate.",
            },
            "polya": {
                "hash": _hash_file(repo_root / polya_ref),
                "source_ref": polya_ref,
                "research_proxy": True,
                "note": "Current research slice hashes the lens answer-core artifact as a proxy for future cached lens substrate.",
            },
        },
        "conversation_ir_hash": {
            "hash": _hash_text(case_id),
            "source": "research_fixture_case_id",
            "note": "Static research fixtures do not carry live ConversationIR.",
        },
        "problem_state_hash": _hash_file(repo_root / problem_state_ref),
        "rendered_hybrid_anchor_hash": _hash_file(repo_root / rendered_ref),
        "v60_selected_item_hashes": {
            "state": "provided" if v60_selected_item_hashes else "not_attached_to_research_fixture",
            "hashes": sorted(v60_selected_item_hashes),
        },
        "safety_profile_flags": _safety_profile_flags(case_id),
        "step6_prompt_contract_version": STEP6_PROMPT_CONTRACT_VERSION,
    }


def _cache_read(*, cache_mode: str, cache_hit: bool) -> dict[str, object]:
    if cache_mode == "off":
        miss_behavior = "card_deck_disabled"
        cold_path_policy = "no_card_deck_path"
    elif cache_hit:
        miss_behavior = "not_applicable_cache_hit"
        cold_path_policy = "use_compiled_cached_deck"
    elif cache_mode == "runtime_cached_only":
        miss_behavior = "stand_down_to_current_step6"
        cold_path_policy = "record_cache_miss_without_live_generation"
    elif cache_mode == "experimental":
        miss_behavior = "cold_fill_allowed_behind_flag"
        cold_path_policy = "bounded_live_generation_allowed_for_experiment"
    else:
        miss_behavior = "live_card_generation_allowed"
        cold_path_policy = "research_only_generation_allowed"
    return {
        "cache_mode": cache_mode,
        "cache_hit": cache_hit,
        "miss_behavior": miss_behavior,
        "cold_path_policy": cold_path_policy,
    }


def _cost_envelope(*, cache_mode: str, cache_hit: bool) -> dict[str, object]:
    live_generation = cache_mode in {"research", "experimental"} and not cache_hit
    if live_generation:
        net_new_calls = 2
    else:
        net_new_calls = 0
    return {
        "net_new_llm_calls": net_new_calls,
        "live_card_generation_allowed": live_generation,
        "normal_runtime_reviewer_calls": 0,
        "token_cost_read": (
            "Step 6 receives added private deck context only on cache hit; "
            "runtime miss adds no deck context."
        ),
    }


def _runtime_effect(
    *,
    cache_mode: str,
    cache_hit: bool,
    miss_behavior: str,
) -> dict[str, object]:
    presented = cache_mode != "off" and (cache_hit or cache_mode in {"research", "experimental"})
    if cache_mode == "runtime_cached_only" and not cache_hit:
        records_issue = "card_deck_cache_miss"
        fallback = "current_step6_without_card_deck"
    elif cache_mode == "off":
        records_issue = ""
        fallback = "card_deck_disabled"
    elif cache_hit:
        records_issue = ""
        fallback = "compiled_card_deck_available"
    else:
        records_issue = "cold_fill_used"
        fallback = miss_behavior
    return {
        "step6_card_deck_presented": presented,
        "records_issue": records_issue,
        "fallback_behavior": fallback,
    }


def _validate_key_material(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    fields = set(value)
    if fields != REQUIRED_KEY_MATERIAL_FIELDS:
        missing = sorted(REQUIRED_KEY_MATERIAL_FIELDS - fields)
        extra = sorted(fields - REQUIRED_KEY_MATERIAL_FIELDS)
        if missing:
            yield f"{path}: missing key material fields: {', '.join(missing)}"
        if extra:
            yield f"{path}: unknown key material fields: {', '.join(extra)}"
    if not _string(value.get("card_deck_schema_version")):
        yield f"{path / 'card_deck_schema_version'}: must be non-empty"
    if not _string(value.get("deck_builder_version")):
        yield f"{path / 'deck_builder_version'}: must be non-empty"
    if not isinstance(value.get("lens_pack_versions"), dict):
        yield f"{path / 'lens_pack_versions'}: must be an object"
    if not isinstance(value.get("lens_substrate_hashes"), dict):
        yield f"{path / 'lens_substrate_hashes'}: must be an object"
    v60 = value.get("v60_selected_item_hashes")
    if not isinstance(v60, dict):
        yield f"{path / 'v60_selected_item_hashes'}: must be an object"
    elif not isinstance(v60.get("hashes"), list):
        yield f"{path / 'v60_selected_item_hashes' / 'hashes'}: must be a list"


def _validate_compiled_key(payload: dict[str, object], path: Path) -> Iterable[str]:
    key = _string(payload.get("compiled_card_deck_key"))
    if not key.startswith("sha256:"):
        yield f"{path / 'compiled_card_deck_key'}: must start with sha256:"
        return
    material = payload.get("key_material")
    if isinstance(material, dict) and key != _compiled_key(material):
        yield f"{path / 'compiled_card_deck_key'}: must match key_material hash"


def _validate_cache_read(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, CACHE_READ_FIELDS, path)
    yield from _missing_fields(value, CACHE_READ_FIELDS, path)
    if _string(value.get("cache_mode")) not in ALLOWED_CACHE_MODES:
        yield f"{path / 'cache_mode'}: unsupported mode"
    if not isinstance(value.get("cache_hit"), bool):
        yield f"{path / 'cache_hit'}: must be boolean"
    if not _string(value.get("miss_behavior")):
        yield f"{path / 'miss_behavior'}: must be non-empty"
    if not _string(value.get("cold_path_policy")):
        yield f"{path / 'cold_path_policy'}: must be non-empty"


def _validate_cost_envelope(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, COST_ENVELOPE_FIELDS, path)
    yield from _missing_fields(value, COST_ENVELOPE_FIELDS, path)
    if not isinstance(value.get("net_new_llm_calls"), int):
        yield f"{path / 'net_new_llm_calls'}: must be integer"
    if not isinstance(value.get("live_card_generation_allowed"), bool):
        yield f"{path / 'live_card_generation_allowed'}: must be boolean"
    if value.get("normal_runtime_reviewer_calls") != 0:
        yield f"{path / 'normal_runtime_reviewer_calls'}: must be 0"


def _validate_runtime_effect(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, RUNTIME_EFFECT_FIELDS, path)
    yield from _missing_fields(value, RUNTIME_EFFECT_FIELDS, path)
    if not isinstance(value.get("step6_card_deck_presented"), bool):
        yield f"{path / 'step6_card_deck_presented'}: must be boolean"


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


def _validate_runtime_cached_only_policy(
    payload: dict[str, object],
    path: Path,
) -> Iterable[str]:
    cache = payload.get("cache_read")
    cost = payload.get("cost_envelope")
    effect = payload.get("runtime_effect")
    if not isinstance(cache, dict) or not isinstance(cost, dict) or not isinstance(effect, dict):
        return
    if cache.get("cache_mode") == "runtime_cached_only" and cache.get("cache_hit") is False:
        if cache.get("miss_behavior") != "stand_down_to_current_step6":
            yield f"{path / 'cache_read' / 'miss_behavior'}: runtime miss must stand down"
        if cost.get("net_new_llm_calls") != 0:
            yield f"{path / 'cost_envelope' / 'net_new_llm_calls'}: runtime miss must add 0 calls"
        if cost.get("live_card_generation_allowed") is not False:
            yield (
                f"{path / 'cost_envelope' / 'live_card_generation_allowed'}: "
                "runtime miss must not allow live generation"
            )
        if effect.get("step6_card_deck_presented") is not False:
            yield f"{path / 'runtime_effect' / 'step6_card_deck_presented'}: must be false"
        if effect.get("records_issue") != "card_deck_cache_miss":
            yield f"{path / 'runtime_effect' / 'records_issue'}: must record cache miss"


def _compiled_key(key_material: dict[str, object]) -> str:
    encoded = json.dumps(key_material, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(encoded.encode('utf-8')).hexdigest()}"


def _hash_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _hash_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _safety_profile_flags(case_id: str) -> list[str]:
    if "mother" in case_id:
        return ["sensitive_safety", "weak_evidence"]
    if "consultant" in case_id:
        return ["professional_advice", "negative_control"]
    return ["standard_research_case"]


def _unknown_fields(value: dict[str, object], allowed: frozenset[str], path: Path) -> Iterable[str]:
    for field in sorted(set(value) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(value: dict[str, object], required: Iterable[str], path: Path) -> Iterable[str]:
    for field in sorted(set(required) - set(value)):
        yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Existing cost/cache payloads to validate")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--case-id", default="founder-grant-marcus-equity.high-clutter")
    parser.add_argument("--cache-mode", choices=sorted(ALLOWED_CACHE_MODES), default="runtime_cached_only")
    parser.add_argument("--cache-hit", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.paths:
        for path in args.paths:
            validate_cost_cache_contract_file(path)
        return 0
    payload = build_cost_cache_contract(
        case_id=args.case_id,
        repo_root=args.repo_root,
        cache_mode=args.cache_mode,
        cache_hit=args.cache_hit,
    )
    if args.write:
        print(write_cost_cache_contract(payload=payload, out_dir=args.out_dir))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
