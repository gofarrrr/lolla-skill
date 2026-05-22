#!/usr/bin/env python3
"""Research-only visibility policy for card-deck Step 6 replays.

This policy records when Step 6 itself treated non-anchor cards as private or
confirming. It does not decide answer quality; it pairs that deterministic read
with a cognitive comparison result before naming a visible-answer policy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_card_deck_replay_comparisons import (
    load_replay_comparison_payload,
    validate_replay_comparison_payload,
)
from pre_step6_card_deck_replays import (
    CARD_IDS,
    load_card_deck_replay_payload,
    validate_card_deck_replay_payload,
)


SCHEMA_VERSION = "pre_step6_card_deck_visibility_policy.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
POLICY_KIND = "ledger_based_anchor_standdown"
DEFAULT_OUT_DIR = Path("research/pre-step6-card-deck-visibility-policies")
NON_ANCHOR_CARD_IDS = ("bevelin_card", "polya_card")
PRIVATE_OR_CONFIRMING_ROLES = frozenset({"confirming_support", "private_guardrail"})
ALLOWED_VISIBLE_RESULTS = frozenset(
    {
        "anchor_visible_after_cognitive_confirmation",
        "card_deck_visible_after_cognitive_confirmation",
        "retest_required",
    }
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "policy_kind",
        "source_refs",
        "ledger_summary",
        "deterministic_read",
        "cognitive_confirmation",
        "visible_policy",
        "gates",
        "notes",
    }
)
SOURCE_REF_FIELDS = frozenset({"card_deck_replay", "cognitive_comparison"})
LEDGER_ITEM_FIELDS = frozenset(
    {"card_id", "disposition", "novelty_role", "visible_effect"}
)
DETERMINISTIC_READ_FIELDS = frozenset(
    {
        "anchor_standdown_eligible",
        "deterministic_quality_decision",
        "non_anchor_additive_count",
        "non_anchor_private_or_confirming_count",
        "reason",
    }
)
COGNITIVE_CONFIRMATION_FIELDS = frozenset(
    {"status", "reviewer_winner", "reviewer_deck_effect", "reviewer_confidence"}
)
VISIBLE_POLICY_FIELDS = frozenset({"result", "why_this_is_not_deterministic"})
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})


class VisibilityPolicyValidationError(ValueError):
    pass


def build_visibility_policy(*, case_id: str, repo_root: Path) -> dict[str, object]:
    replay_ref = f"research/pre-step6-card-deck-replays/{case_id}.card-deck-replay.v1.json"
    comparison_ref = (
        "research/pre-step6-card-deck-replay-comparisons/"
        f"{case_id}.card-deck-replay-comparison.v1.json"
    )
    replay = load_card_deck_replay_payload(repo_root / replay_ref)
    validate_card_deck_replay_payload(replay, path=repo_root / replay_ref, repo_root=repo_root)
    comparison = load_replay_comparison_payload(repo_root / comparison_ref)
    validate_replay_comparison_payload(comparison, path=repo_root / comparison_ref)
    ledger_summary = _ledger_summary(replay)
    deterministic_read = _deterministic_read(ledger_summary)
    cognitive_confirmation = _cognitive_confirmation(comparison)
    visible_policy = _visible_policy(
        deterministic_read=deterministic_read,
        cognitive_confirmation=cognitive_confirmation,
    )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "case_id": case_id,
        "policy_kind": POLICY_KIND,
        "source_refs": {
            "card_deck_replay": replay_ref,
            "cognitive_comparison": comparison_ref,
        },
        "ledger_summary": ledger_summary,
        "deterministic_read": deterministic_read,
        "cognitive_confirmation": cognitive_confirmation,
        "visible_policy": visible_policy,
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": (
            "Research-only policy. Code records Step 6's own private ledger and "
            "the cognitive comparison result; it does not infer answer quality "
            "from counts."
        ),
    }
    validate_visibility_policy_payload(payload)
    return payload


def load_visibility_policy_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise VisibilityPolicyValidationError(f"{path}: payload must be an object")
    return payload


def validate_visibility_policy_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_visibility_policy_errors(payload, path=Path(path)))
    if errors:
        raise VisibilityPolicyValidationError("; ".join(errors))


def validate_visibility_policy_file(path: Path) -> None:
    validate_visibility_policy_payload(load_visibility_policy_payload(path), path=Path(path))


def iter_visibility_policy_errors(
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
    if _string(payload.get("policy_kind")) != POLICY_KIND:
        yield f"{path / 'policy_kind'}: must be {POLICY_KIND}"
    yield from _validate_source_refs(payload.get("source_refs"), path / "source_refs")
    yield from _validate_ledger_summary(payload.get("ledger_summary"), path / "ledger_summary")
    yield from _validate_deterministic_read(
        payload.get("deterministic_read"),
        path / "deterministic_read",
    )
    yield from _validate_cognitive_confirmation(
        payload.get("cognitive_confirmation"),
        path / "cognitive_confirmation",
    )
    yield from _validate_visible_policy(payload.get("visible_policy"), path / "visible_policy")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def write_visibility_policy(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_visibility_policy_payload(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{_string(payload['case_id'])}.card-deck-visibility-policy.v1.json"
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_path


def _ledger_summary(replay: dict[str, object]) -> list[dict[str, str]]:
    output = replay.get("step6_output")
    if not isinstance(output, dict):
        raise VisibilityPolicyValidationError("step6_output missing")
    ledger = output.get("private_card_consideration_ledger")
    if not isinstance(ledger, list):
        raise VisibilityPolicyValidationError("private_card_consideration_ledger missing")
    summary: list[dict[str, str]] = []
    for item in ledger:
        if not isinstance(item, dict):
            continue
        summary.append(
            {
                "card_id": _string(item.get("card_id")),
                "disposition": _string(item.get("disposition")),
                "novelty_role": _string(item.get("novelty_role")),
                "visible_effect": _string(item.get("visible_effect")),
            }
        )
    return summary


def _deterministic_read(ledger_summary: list[dict[str, str]]) -> dict[str, object]:
    by_id = {item["card_id"]: item for item in ledger_summary}
    non_anchor = [by_id.get(card_id, {}) for card_id in NON_ANCHOR_CARD_IDS]
    additive_count = sum(
        1 for item in non_anchor if _string(item.get("novelty_role")) == "additive_pressure"
    )
    private_or_confirming_count = sum(
        1
        for item in non_anchor
        if _string(item.get("novelty_role")) in PRIVATE_OR_CONFIRMING_ROLES
    )
    eligible = additive_count == 0 and private_or_confirming_count == len(NON_ANCHOR_CARD_IDS)
    return {
        "anchor_standdown_eligible": eligible,
        "deterministic_quality_decision": False,
        "non_anchor_additive_count": additive_count,
        "non_anchor_private_or_confirming_count": private_or_confirming_count,
        "reason": (
            "Step 6 marked all non-anchor cards as private or confirming."
            if eligible
            else "Step 6 marked at least one non-anchor card as additive pressure."
        ),
    }


def _cognitive_confirmation(comparison: dict[str, object]) -> dict[str, str]:
    output = comparison.get("reviewer_output")
    blind_map = comparison.get("blind_map")
    if not isinstance(output, dict) or not isinstance(blind_map, dict):
        raise VisibilityPolicyValidationError("comparison reviewer output missing")
    winner_label = _string(output.get("winner_label"))
    if winner_label == "tie":
        reviewer_winner = "tie"
    else:
        reviewer_winner = _string(blind_map.get(winner_label))
    if reviewer_winner == "clean_hybrid":
        status = "anchor_confirmed_by_reviewer"
    elif reviewer_winner == "card_deck_replay":
        status = "deck_confirmed_by_reviewer"
    elif reviewer_winner == "tie":
        status = "tie_requires_retest_or_policy_choice"
    else:
        status = "unknown_reviewer_result"
    return {
        "status": status,
        "reviewer_winner": reviewer_winner,
        "reviewer_deck_effect": _string(output.get("deck_effect")),
        "reviewer_confidence": _string(output.get("confidence")),
    }


def _visible_policy(
    *,
    deterministic_read: dict[str, object],
    cognitive_confirmation: dict[str, str],
) -> dict[str, str]:
    eligible = deterministic_read.get("anchor_standdown_eligible") is True
    status = cognitive_confirmation.get("status")
    if eligible and status == "anchor_confirmed_by_reviewer":
        result = "anchor_visible_after_cognitive_confirmation"
    elif status == "deck_confirmed_by_reviewer":
        result = "card_deck_visible_after_cognitive_confirmation"
    else:
        result = "retest_required"
    return {
        "result": result,
        "why_this_is_not_deterministic": (
            "The deterministic read only records Step 6 ledger roles. The visible "
            "answer policy requires the cognitive comparison result before it can "
            "prefer anchor or card-deck replay."
        ),
    }


def _validate_source_refs(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: source_refs must be an object"
        return
    yield from _unknown_fields(value, SOURCE_REF_FIELDS, path)
    yield from _missing_fields(value, tuple(SOURCE_REF_FIELDS), path)
    for field in SOURCE_REF_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_ledger_summary(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list):
        yield f"{path}: ledger_summary must be a list"
        return
    ids = [_string(item.get("card_id")) if isinstance(item, dict) else "" for item in value]
    if tuple(ids) != CARD_IDS:
        yield f"{path}: ledger must account for all card ids in order"
    for index, item in enumerate(value):
        item_path = path / f"[{index}]"
        if not isinstance(item, dict):
            yield f"{item_path}: ledger item must be an object"
            continue
        yield from _unknown_fields(item, LEDGER_ITEM_FIELDS, item_path)
        yield from _missing_fields(item, tuple(LEDGER_ITEM_FIELDS), item_path)
        if any(field not in item for field in LEDGER_ITEM_FIELDS):
            continue
        for field in LEDGER_ITEM_FIELDS:
            if not _string(item.get(field)).strip():
                yield f"{item_path / field}: must be non-empty"


def _validate_deterministic_read(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: deterministic_read must be an object"
        return
    yield from _unknown_fields(value, DETERMINISTIC_READ_FIELDS, path)
    yield from _missing_fields(value, tuple(DETERMINISTIC_READ_FIELDS), path)
    if value.get("deterministic_quality_decision") is not False:
        yield f"{path / 'deterministic_quality_decision'}: must be false"
    for field in ("anchor_standdown_eligible",):
        if not isinstance(value.get(field), bool):
            yield f"{path / field}: must be boolean"
    for field in ("non_anchor_additive_count", "non_anchor_private_or_confirming_count"):
        if not isinstance(value.get(field), int):
            yield f"{path / field}: must be integer"
    if not _string(value.get("reason")).strip():
        yield f"{path / 'reason'}: must be non-empty"


def _validate_cognitive_confirmation(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: cognitive_confirmation must be an object"
        return
    yield from _unknown_fields(value, COGNITIVE_CONFIRMATION_FIELDS, path)
    yield from _missing_fields(value, tuple(COGNITIVE_CONFIRMATION_FIELDS), path)
    for field in COGNITIVE_CONFIRMATION_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_visible_policy(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: visible_policy must be an object"
        return
    yield from _unknown_fields(value, VISIBLE_POLICY_FIELDS, path)
    yield from _missing_fields(value, tuple(VISIBLE_POLICY_FIELDS), path)
    if _string(value.get("result")) not in ALLOWED_VISIBLE_RESULTS:
        yield f"{path / 'result'}: unknown result"
    if not _string(value.get("why_this_is_not_deterministic")).strip():
        yield f"{path / 'why_this_is_not_deterministic'}: must be non-empty"


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
    raise VisibilityPolicyValidationError("provide --case-id or --all")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            validate_visibility_policy_file(path)
        return 0

    outputs: list[Path] = []
    for case_id in _parse_case_ids(args):
        payload = build_visibility_policy(case_id=case_id, repo_root=args.repo_root)
        output = write_visibility_policy(payload=payload, out_dir=args.out_dir)
        outputs.append(output)
        print(output)
    if outputs:
        print(f"wrote {len(outputs)} visibility policy artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
