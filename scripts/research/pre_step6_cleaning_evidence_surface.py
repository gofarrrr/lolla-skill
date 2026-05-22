#!/usr/bin/env python3
"""Build a research-only evidence surface for pre-Step-6 cleaning slices.

The surface aggregates cleaning-lane artifacts into a human-readable pattern
view. It may nominate candidates for human review. It does not graduate cards,
change visibility, update runtime, or edit SKILL.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence


SCHEMA_VERSION = "pre_step6_cleaning_evidence_surface.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "evidence_surface_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-cleaning-evidence-surface")

CONSULTANT_REPLAY_REF = (
    "research/pre-step6-consultant-cleaning-variant-replay/"
    "consultant-cleaning-variant-replay-result.v1.json"
)
CONSULTANT_PATCH_REF = (
    "research/pre-step6-consultant-anchor-boundary-patch-probe/"
    "consultant-anchor-boundary-patch-probe-result.v1.json"
)
PHD_REVIEW_REF = (
    "research/pre-step6-phd-kimi-variance-cleaning-review/"
    "phd-kimi-variance-cleaning-review-result.v1.json"
)
CONSULTANT_CASE_ID = "mid-level-consultant-report-2"
PHD_CASE_ID = "third-year-phd-student.v2.v60-off"
CONSULTANT_REVERSIBILITY_TEXT = (
    "keep the first moves reversible until counsel guides the next action"
)
CONSULTANT_CARD_IDS = (
    "counsel_independence_and_channel_bias_card",
    "wednesday_tripwire_preservation_card",
    "reversibility_until_counsel_boundary_card",
)
PHD_CARD_IDS = (
    "bounded_probe_not_commitment_card",
    "single_cell_collaborator_feasibility_card",
    "fallback_reentry_readiness_card",
    "visible_stop_date_conditions_card",
)


class CleaningEvidenceSurfaceError(ValueError):
    pass


def build_cleaning_evidence_surface(*, root: Path) -> dict[str, object]:
    consultant_replay = _read_json(root / CONSULTANT_REPLAY_REF)
    consultant_patch = _read_json(root / CONSULTANT_PATCH_REF)
    phd_review = _read_json(root / PHD_REVIEW_REF)

    surface = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "source_refs": {
            "consultant_cleaning_variant_replay": CONSULTANT_REPLAY_REF,
            "consultant_anchor_boundary_patch_probe": CONSULTANT_PATCH_REF,
            "phd_kimi_variance_cleaning_review": PHD_REVIEW_REF,
        },
        "principles": {
            "code_may_nominate": True,
            "humans_decide": True,
            "automatic_graduation_allowed": False,
            "runtime_visibility_change_allowed": False,
        },
        "case_summaries": [
            _consultant_summary(consultant_replay, consultant_patch),
            _phd_summary(phd_review),
        ],
        "atom_rows": [
            *_consultant_atom_rows(consultant_replay, consultant_patch),
            *_phd_atom_rows(phd_review),
        ],
        "graduation_candidates": _graduation_candidates(consultant_replay, consultant_patch),
        "global_read": {
            "evidence_surface_ready": True,
            "cases_covered": [CONSULTANT_CASE_ID, PHD_CASE_ID],
            "automatic_graduation_allowed": False,
            "runtime_promotion": "blocked",
            "skill_update": "blocked",
            "closeout_decision_read": "ready_for_closeout_not_runtime_promotion",
        },
    }
    validate_cleaning_evidence_surface(surface)
    return surface


def write_cleaning_evidence_surface(*, surface: dict[str, object], out_dir: Path) -> Path:
    validate_cleaning_evidence_surface(surface)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "cleaning-evidence-surface.v1.json"
    path.write_text(json.dumps(surface, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_cleaning_evidence_surface_markdown(*, surface: dict[str, object], out_dir: Path) -> Path:
    validate_cleaning_evidence_surface(surface)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "cleaning-evidence-surface.md"
    path.write_text(render_cleaning_evidence_surface_markdown(surface), encoding="utf-8")
    return path


def render_cleaning_evidence_surface_markdown(surface: Mapping[str, object]) -> str:
    validate_cleaning_evidence_surface(dict(surface))
    lines = [
        "# Cleaning Evidence Surface",
        "",
        "Status: research-only. Runtime dormant. SKILL.md unchanged.",
        "",
        "Code may nominate; humans decide.",
        "",
        "## Graduation Candidates",
        "",
    ]
    candidates = surface.get("graduation_candidates")
    if isinstance(candidates, list) and candidates:
        for candidate in candidates:
            if not isinstance(candidate, Mapping):
                continue
            lines.extend(
                [
                    f"- `{candidate.get('case_id')}` / `{candidate.get('pressure_atom_id')}`",
                    f"  - Atom: {candidate.get('pressure_atom_text')}",
                    f"  - Basis: {candidate.get('basis')}",
                    f"  - Status: `{candidate.get('status')}`",
                    f"  - Next: `{candidate.get('next_investigation')}`",
                ]
            )
    else:
        lines.append("- None.")
    lines.extend(["", "## Atom Rows", ""])
    for row in surface.get("atom_rows", []):
        if not isinstance(row, Mapping):
            continue
        lines.append(
            "- `{case_id}` / `{atom}`: {count}/{total} additive "
            "({rate:.3f}), `{read}`, `{nomination}`".format(
                case_id=row.get("case_id"),
                atom=row.get("pressure_atom_id"),
                count=int(row.get("additive_count", 0)),
                total=int(row.get("sample_count", 0)),
                rate=float(row.get("additive_rate", 0.0)),
                read=row.get("evidence_read"),
                nomination=row.get("nomination"),
            )
        )
    lines.extend(["", "## Case Summaries", ""])
    for summary in surface.get("case_summaries", []):
        if not isinstance(summary, Mapping):
            continue
        lines.append(
            "- `{case_id}`: `{read}`; protected payload {protected}/{samples}".format(
                case_id=summary.get("case_id"),
                read=summary.get("cleaning_read"),
                protected=summary.get("protected_payload_all_present_count"),
                samples=summary.get("sample_count"),
            )
        )
    lines.extend(["", "## Boundary", ""])
    lines.extend(
        [
            "- This surface does not decide wisdom.",
            "- This surface does not graduate cards upstream automatically.",
            "- This surface does not change runtime visibility.",
            "- This surface exists so humans can read patterns without opening raw JSON.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_cleaning_evidence_surface(surface: dict[str, object]) -> None:
    errors = list(iter_cleaning_evidence_surface_errors(surface))
    if errors:
        raise CleaningEvidenceSurfaceError("; ".join(errors))


def iter_cleaning_evidence_surface_errors(surface: dict[str, object]) -> Iterable[str]:
    required = {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "source_refs",
        "principles",
        "case_summaries",
        "atom_rows",
        "graduation_candidates",
        "global_read",
    }
    if not isinstance(surface, dict):
        yield "surface must be object"
        return
    missing = sorted(required - set(surface))
    if missing:
        yield f"missing fields: {missing}"
        return
    if surface.get("schema_version") != SCHEMA_VERSION:
        yield "schema_version mismatch"
    if surface.get("status") != STATUS:
        yield "status must be research_only"
    if surface.get("runtime_policy") != RUNTIME_POLICY:
        yield "runtime_policy must be runtime_dormant"
    if surface.get("promotion_effect") != "none_research_only":
        yield "promotion_effect must be none_research_only"
    principles = surface.get("principles")
    if not isinstance(principles, dict):
        yield "principles must be object"
    elif principles.get("automatic_graduation_allowed") is not False:
        yield "automatic graduation must remain blocked"
    if not isinstance(surface.get("case_summaries"), list) or not surface["case_summaries"]:
        yield "case_summaries must be non-empty list"
    if not isinstance(surface.get("atom_rows"), list) or not surface["atom_rows"]:
        yield "atom_rows must be non-empty list"
    for candidate in surface.get("graduation_candidates", []):
        if not isinstance(candidate, dict):
            yield "graduation candidate must be object"
            continue
        if candidate.get("status") != "human_review_required":
            yield "graduation candidates must require human review"
    global_read = surface.get("global_read")
    if not isinstance(global_read, dict):
        yield "global_read must be object"
    elif global_read.get("runtime_promotion") != "blocked" or global_read.get("skill_update") != "blocked":
        yield "runtime and skill updates must remain blocked"


def _consultant_summary(
    replay: Mapping[str, object],
    patch: Mapping[str, object],
) -> dict[str, object]:
    replay_aggregate = _mapping(replay.get("aggregate"))
    patch_aggregate = _mapping(patch.get("aggregate"))
    return {
        "case_id": CONSULTANT_CASE_ID,
        "case_shape": "sensitive_safety_legal",
        "sample_count": int(patch_aggregate.get("sample_count", 0)),
        "protected_payload_all_present_count": int(
            patch_aggregate.get("protected_payload_all_present_count", 0)
        ),
        "cleaning_read": "single_atom_graduation_candidate",
        "before_patch_additive_count": int(replay_aggregate.get("micro_card_additive_count", 0)),
        "after_patch_additive_count": int(patch_aggregate.get("micro_card_additive_count", 0)),
        "next_investigation": str(patch_aggregate.get("next_investigation", "")),
    }


def _phd_summary(review: Mapping[str, object]) -> dict[str, object]:
    aggregate = _mapping(review.get("aggregate"))
    return {
        "case_id": PHD_CASE_ID,
        "case_shape": "sequencing_problem_shape",
        "sample_count": int(aggregate.get("sample_count", 0)),
        "protected_payload_all_present_count": int(
            aggregate.get("protected_payload_all_present_count", 0)
        ),
        "cleaning_read": "distributed_atomic_discrimination",
        "atomic_discrimination_read": str(aggregate.get("atomic_discrimination_read", "")),
        "next_investigation": "none_before_closeout",
    }


def _consultant_atom_rows(
    replay: Mapping[str, object],
    patch: Mapping[str, object],
) -> list[dict[str, object]]:
    replay_results = _case_results(replay)
    patch_aggregate = _mapping(patch.get("aggregate"))
    sample_count = len(replay_results)
    rows = []
    for card_id in CONSULTANT_CARD_IDS:
        additive_count = sum(
            1 for row in replay_results if card_id in _strings(row.get("used_micro_cards"))
        )
        evidence_read = (
            "graduation_candidate"
            if card_id == "reversibility_until_counsel_boundary_card"
            and patch_aggregate.get("upstream_pressure_carried") == "yes"
            else "private_or_confirming"
        )
        nomination = "human_review_required" if evidence_read == "graduation_candidate" else "no_nomination"
        rows.append(
            _atom_row(
                case_id=CONSULTANT_CASE_ID,
                atom_id=card_id,
                additive_count=additive_count,
                sample_count=sample_count,
                evidence_read=evidence_read,
                nomination=nomination,
            )
        )
    return rows


def _phd_atom_rows(review: Mapping[str, object]) -> list[dict[str, object]]:
    aggregate = _mapping(review.get("aggregate"))
    card_counts = _mapping(aggregate.get("card_additive_counts"))
    sample_count = int(aggregate.get("sample_count", 0))
    return [
        _atom_row(
            case_id=PHD_CASE_ID,
            atom_id=card_id,
            additive_count=int(card_counts.get(card_id, 0)),
            sample_count=sample_count,
            evidence_read="distributed_pressure_atom",
            nomination="watch_not_graduate",
        )
        for card_id in PHD_CARD_IDS
    ]


def _graduation_candidates(
    replay: Mapping[str, object],
    patch: Mapping[str, object],
) -> list[dict[str, object]]:
    replay_aggregate = _mapping(replay.get("aggregate"))
    patch_aggregate = _mapping(patch.get("aggregate"))
    if (
        int(replay_aggregate.get("micro_card_additive_count", 0)) >= 4
        and patch_aggregate.get("upstream_pressure_carried") == "yes"
    ):
        return [
            {
                "case_id": CONSULTANT_CASE_ID,
                "pressure_atom_id": "reversibility_until_counsel_boundary_card",
                "pressure_atom_text": CONSULTANT_REVERSIBILITY_TEXT,
                "basis": (
                    "4/6 additive before anchor patch; 1/6 additive after patched anchor; "
                    "protected payload preserved 6/6"
                ),
                "status": "human_review_required",
                "next_investigation": str(patch_aggregate.get("next_investigation", "")),
            }
        ]
    return []


def _atom_row(
    *,
    case_id: str,
    atom_id: str,
    additive_count: int,
    sample_count: int,
    evidence_read: str,
    nomination: str,
) -> dict[str, object]:
    rate = round(additive_count / sample_count, 3) if sample_count else 0.0
    return {
        "case_id": case_id,
        "pressure_atom_id": atom_id,
        "additive_count": additive_count,
        "sample_count": sample_count,
        "additive_rate": rate,
        "evidence_read": evidence_read,
        "nomination": nomination,
    }


def _case_results(payload: Mapping[str, object]) -> list[Mapping[str, object]]:
    rows = payload.get("case_results")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, Mapping)]


def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str)]


def _read_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise CleaningEvidenceSurfaceError(f"{path}: expected JSON object")
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    surface = build_cleaning_evidence_surface(root=Path.cwd())
    if args.write:
        json_path = write_cleaning_evidence_surface(surface=surface, out_dir=args.out_dir)
        md_path = write_cleaning_evidence_surface_markdown(surface=surface, out_dir=args.out_dir)
        print(json_path)
        print(md_path)
    else:
        print(json.dumps(surface, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
