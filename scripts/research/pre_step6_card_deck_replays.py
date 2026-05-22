#!/usr/bin/env python3
"""Research-only Step 6 replay from a private card deck."""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_raw_artifacts import validate_public_answer_hygiene
from pre_step6_step6_card_deck import (
    CARD_IDS,
    DEFAULT_OUT_DIR as DEFAULT_DECK_DIR,
    build_step6_card_deck,
    load_step6_card_deck_payload,
    render_step6_card_deck,
    validate_step6_card_deck_payload,
)


SCHEMA_VERSION = "pre_step6_card_deck_replay.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
REPLAY_MODE = "manual_live_step6_from_card_deck"
DEFAULT_OUT_DIR = Path("research/pre-step6-card-deck-replays")
ALLOWED_DISPOSITIONS = frozenset(
    {"used", "rejected", "deferred", "combined", "private_guardrail"}
)
ALLOWED_NOVELTY_ROLES = frozenset(
    {"visible_backbone", "additive_pressure", "confirming_support", "private_guardrail"}
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "replay_mode",
        "source_card_deck",
        "provider_metadata",
        "step6_output",
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
STEP6_OUTPUT_FIELDS = frozenset({"answer_core", "private_card_consideration_ledger"})
LEDGER_FIELDS = frozenset(
    {"card_id", "disposition", "novelty_role", "why", "visible_effect"}
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
PRIVATE_LABEL_TERMS = (
    "bevelin",
    "polya",
    "clean hybrid",
    "private card",
    "card deck",
    "card_id",
    "consideration ledger",
)


class CardDeckReplayValidationError(ValueError):
    pass


def build_step6_replay_prompts(deck_payload: dict[str, object]) -> dict[str, str]:
    validate_step6_card_deck_payload(deck_payload)
    rendered_deck = render_step6_card_deck(deck_payload)
    system_prompt = (
        "You are Step 6, the primary reasoning voice. The card deck is private "
        "context, not an answer template and not a command. Use, reject, defer, "
        "or combine the cards after serious consideration. Your public answer "
        "must be ordinary language and must not expose private card labels, source "
        "names, ids, or mechanics. Return strict JSON only."
    )
    user_prompt = "\n\n".join(
        [
            rendered_deck,
            "TASK",
            (
                "Write a decision-useful answer_core that reflects your own Step 6 "
                "judgment: as short as possible, but no shorter. The clean hybrid "
                "anchor can remain the visible backbone when it already carries the "
                "best sequence. Do not compress away concrete tripwires, conditions, "
                "actor-specific steps, or irreversible-risk distinctions merely to be "
                "concise. "
                "Do not write a full Lolla transcript section. Do not mention private "
                "labels. Use the cards only when they improve the answer. You should "
                "go beyond the obvious if a card reveals useful pressure, but you may "
                "reject or defer anything that does not help. A card can also become "
                "a private guardrail: considered seriously, kept out of the public "
                "answer, and used only to prevent overreach or over-compression."
                " The ledger is where card consideration lives. Do not lengthen "
                "the public answer merely to prove that every card was considered; "
                "make the public answer longer only when a card adds concrete "
                "decision pressure the anchor does not already carry. In a "
                "sensitive safety or legal context, visible enrichment must add a "
                "concrete safeguard, tripwire, or channel distinction; otherwise "
                "keep it private. Do not shorten by deleting concrete anchor payload: "
                "named channels or resources, communication boundaries, dated windows, "
                "gates, actor sequence, tripwires, and evidence checks should survive "
                "unless you have a specific reason to replace them. Preserve structural "
                "separation when the anchor separates distinct decision domains; do not "
                "compress unrelated moves into one paragraph. Do not use public machinery terms "
                "that Lolla hygiene forbids, including bundle, lane, artifact, worker, "
                "lens, card, portfolio, and attention map."
            ),
            "RESPONSE JSON SHAPE",
            json.dumps(
                {
                    "answer_core": "Public-clean answer core, no private labels.",
                    "private_card_consideration_ledger": [
                        {
                            "card_id": "clean_hybrid_card | bevelin_card | polya_card",
                            "disposition": (
                                "used | rejected | deferred | combined | private_guardrail"
                            ),
                            "novelty_role": (
                                "visible_backbone | additive_pressure | "
                                "confirming_support | private_guardrail"
                            ),
                            "why": "Private rationale for the disposition.",
                            "visible_effect": (
                                "What changed in the answer, or 'none' if kept private."
                            ),
                        }
                    ],
                },
                indent=2,
            ),
        ]
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}


def load_card_deck_replay_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CardDeckReplayValidationError(f"{path}: payload must be an object")
    return payload


def validate_card_deck_replay_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
) -> None:
    errors = list(
        iter_card_deck_replay_errors(payload, path=Path(path), repo_root=repo_root)
    )
    if errors:
        raise CardDeckReplayValidationError("; ".join(errors))


def validate_card_deck_replay_file(path: Path, *, repo_root: Path | None = None) -> None:
    validate_card_deck_replay_payload(
        load_card_deck_replay_payload(path),
        path=Path(path),
        repo_root=repo_root,
    )


def iter_card_deck_replay_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
    repo_root: Path | None = None,
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
    case_id = _string(payload.get("case_id"))
    if not case_id.strip():
        yield f"{path / 'case_id'}: must be non-empty"
    if _string(payload.get("replay_mode")) != REPLAY_MODE:
        yield f"{path / 'replay_mode'}: must be {REPLAY_MODE}"
    yield from _validate_source_card_deck(
        payload.get("source_card_deck"),
        case_id=case_id,
        path=path / "source_card_deck",
        repo_root=repo_root,
    )
    yield from _validate_provider_metadata(
        payload.get("provider_metadata"),
        path / "provider_metadata",
    )
    yield from _validate_step6_output(payload.get("step6_output"), path / "step6_output")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def run_live_replay(
    *,
    case_id: str,
    repo_root: Path,
    provider: str,
    model: str,
    env_file: Path | None,
    deck_dir: Path,
    out_dir: Path,
    dry_run: bool,
) -> Path | None:
    if env_file is not None:
        _load_env_file(env_file)
    if model:
        os.environ["LOLLA_OPENROUTER_MODEL"] = model

    deck_payload = build_step6_card_deck(case_id=case_id, repo_root=repo_root)
    artifact_slug = _artifact_slug(case_id)
    deck_dir.mkdir(parents=True, exist_ok=True)
    deck_path = deck_dir / f"{artifact_slug}.step6-card-deck.v1.json"
    deck_path.write_text(
        json.dumps(deck_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    prompts = build_step6_replay_prompts(deck_payload)
    if dry_run:
        print(prompts["user_prompt"])
        return None

    sys.path.insert(0, str(repo_root / "engine"))
    sys.path.insert(0, str(repo_root))
    from system_b.boundary_provider import load_boundary_client_from_env  # noqa: PLC0415

    client = load_boundary_client_from_env(provider)
    reviewer_output, metadata = client.run_json_with_metadata(
        prompts["system_prompt"],
        prompts["user_prompt"],
        stage="pre_step6_card_deck_replay",
        tendency_id=case_id,
    )
    provider_metadata = _provider_metadata_dict(metadata)
    if _string(provider_metadata.get("status")) != "ok":
        raise CardDeckReplayValidationError(
            "live Step 6 replay failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "case_id": case_id,
        "replay_mode": REPLAY_MODE,
        "source_card_deck": str(deck_path.relative_to(repo_root)),
        "provider_metadata": provider_metadata,
        "step6_output": _normalize_step6_output(reviewer_output),
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Live research replay from full Step 6 private card deck. This records "
            "Step 6's own card dispositions; code did not select the winning card."
        ),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{artifact_slug}.card-deck-replay.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    validate_card_deck_replay_file(out_path, repo_root=repo_root)
    return out_path


def _validate_source_card_deck(
    value: object,
    *,
    case_id: str,
    path: Path,
    repo_root: Path | None,
) -> Iterable[str]:
    ref = _string(value)
    if not ref.strip():
        yield f"{path}: must be non-empty"
        return
    if repo_root is None:
        return
    deck_path = repo_root / ref
    if not deck_path.exists():
        yield f"{path}: source card deck missing"
        return
    deck_payload = load_step6_card_deck_payload(deck_path)
    validate_step6_card_deck_payload(deck_payload, path=deck_path)
    if _string(deck_payload.get("case_id")) != case_id:
        yield f"{path}: source card deck case_id mismatch"


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
        value.get("private_card_consideration_ledger"),
        path / "private_card_consideration_ledger",
    )


def _validate_ledger(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: private_card_consideration_ledger must be a list"
        return
    ids = [
        _string(item.get("card_id")) if isinstance(item, dict) else ""
        for item in value
    ]
    if tuple(ids) != CARD_IDS:
        yield f"{path}: ledger must account for clean_hybrid_card, bevelin_card, polya_card"
    for index, item in enumerate(value):
        item_path = path / f"[{index}]"
        if not isinstance(item, dict):
            yield f"{item_path}: ledger item must be an object"
            continue
        yield from _unknown_fields(item, LEDGER_FIELDS, item_path)
        yield from _missing_fields(item, tuple(LEDGER_FIELDS), item_path)
        if any(field not in item for field in LEDGER_FIELDS):
            continue
        if _string(item.get("disposition")) not in ALLOWED_DISPOSITIONS:
            yield f"{item_path / 'disposition'}: unknown disposition"
        if _string(item.get("novelty_role")) not in ALLOWED_NOVELTY_ROLES:
            yield f"{item_path / 'novelty_role'}: unknown novelty_role"
        for field in ("why", "visible_effect"):
            if not _string(item.get(field)).strip():
                yield f"{item_path / field}: must be non-empty"


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


def _normalize_step6_output(value: dict[str, object]) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    ledger = value.get("private_card_consideration_ledger")
    if not isinstance(ledger, list):
        ledger = []
    by_id = {
        _string(item.get("card_id")): item
        for item in ledger
        if isinstance(item, dict)
    }
    normalized_ledger: list[dict[str, str]] = []
    for card_id in CARD_IDS:
        item = by_id.get(card_id, {})
        normalized_ledger.append(
            {
                "card_id": card_id,
                "disposition": _string(item.get("disposition")) or "deferred",
                "novelty_role": _string(item.get("novelty_role"))
                or (
                    "visible_backbone"
                    if card_id == "clean_hybrid_card"
                    else "confirming_support"
                ),
                "why": _string(item.get("why")) or "Model did not explain this card.",
                "visible_effect": _string(item.get("visible_effect")) or "none",
            }
        )
    return {
        "answer_core": _string(value.get("answer_core")),
        "private_card_consideration_ledger": normalized_ledger,
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
        raise CardDeckReplayValidationError(f"env file missing: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _artifact_slug(case_id: str) -> str:
    return case_id


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
    raise CardDeckReplayValidationError("provide --case-id or --all")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", default="")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--deck-dir", type=Path, default=DEFAULT_DECK_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            validate_card_deck_replay_file(path, repo_root=args.repo_root)
        return 0

    outputs: list[Path] = []
    for case_id in _parse_case_ids(args):
        output = run_live_replay(
            case_id=case_id,
            repo_root=args.repo_root,
            provider=args.provider,
            model=args.model,
            env_file=args.env_file,
            deck_dir=args.deck_dir,
            out_dir=args.out_dir,
            dry_run=args.dry_run,
        )
        if output is not None:
            outputs.append(output)
            print(output)
    if outputs:
        print(f"wrote {len(outputs)} card deck replay(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
