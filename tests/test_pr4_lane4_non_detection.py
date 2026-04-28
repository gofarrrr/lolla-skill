"""PR 4 — Lane 4 dimension non-detection reasoning.

The dimension-detection LLM call previously returned only the dimensions
it judged structurally present (typically 7-10 of 15). The other 5-8 were
silently absent. This PR enumerates all 15 with `present: bool` plus a
`presence_reason` so the audit memo can ask the LLM "why does dimension X
not apply" — closing the largest visibility gap in Lane 4.

The fix is two-layer:
  1. Prompt change — instruct the LLM to enumerate all 15.
  2. Parser change — preserve the new shape, default present=True for
     backwards compatibility, ensure `_MAX_GAPS=5` operates only on
     present-and-uncovered dimensions.

This module covers the parser-side TDD slice. Prompt compliance is
validated via the calibration scripts at scripts/test_lane4*.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.structural_coverage import (
    DetectedDimension,
    _MAX_GAPS,
    _parse_dimension_detection,
)


def _new_shape_payload() -> dict:
    """All 15 dimensions, mix of present:true / present:false rows."""
    detected = [
        # 7 present dimensions (4 covered, 3 gaps)
        ("incentive-alignment", True, False, "Senior partner has revenue interest", "high stakes"),
        ("uncertainty-type", True, False, "Outcome unknowable from current evidence", "decisive"),
        ("commitment-reversibility", True, False, "Lock-in once announced", "load-bearing"),
        ("information-quality", True, True, "Thorough source review present", ""),
        ("stakeholder-alignment", True, True, "Junior staff voices considered", ""),
        ("risk-response", True, True, "Downside framed", ""),
        ("scope-boundary", True, True, "Boundaries explicit", ""),
    ]
    not_present = [
        ("behavioral-intervention", "No behavior change required by this decision."),
        ("causal-diagnosis", "Question is decision-evaluation, not root-cause analysis."),
        ("competitive-dynamics", "No external competitor reaction is a load-bearing factor."),
        ("existing-vs-new", "Decision doesn't allocate between existing vs new."),
        ("feedback-system-dynamics", "No feedback loops or non-linear dynamics implicated."),
        ("resource-allocation", "Budget allocation is not the structural tension."),
        ("scaling-dynamics", "Question doesn't depend on scale-related effects."),
        ("timing-sequencing", "No deadline or order-dependent constraint surfaced."),
    ]
    payload_dims = []
    for d_id, present, covered, evidence, materiality in detected:
        payload_dims.append({
            "dimension_id": d_id,
            "dimension_name": d_id.replace("-", " ").title(),
            "present": present,
            "covered": covered,
            "coverage_evidence": evidence,
            "materiality_note": materiality,
            "presence_reason": "",
        })
    for d_id, reason in not_present:
        payload_dims.append({
            "dimension_id": d_id,
            "dimension_name": d_id.replace("-", " ").title(),
            "present": False,
            "presence_reason": reason,
        })
    return {"dimensions": payload_dims}


def test_parser_handles_all_15_with_present_flag():
    parsed = _parse_dimension_detection(_new_shape_payload())

    # Every dimension lands in the parsed list
    assert len(parsed) == 15
    by_id = {d.dimension_id: d for d in parsed}

    # The 8 not-present dimensions retain their reasons
    not_present = [d for d in parsed if not d.present]
    assert len(not_present) == 8
    assert by_id["behavioral-intervention"].presence_reason.startswith("No behavior change")
    assert by_id["competitive-dynamics"].presence_reason.startswith("No external")

    # The 7 present dimensions carry coverage evidence
    present = [d for d in parsed if d.present]
    assert len(present) == 7
    assert by_id["incentive-alignment"].covered is False
    assert by_id["incentive-alignment"].coverage_evidence == "Senior partner has revenue interest"


def test_parser_does_not_crash_when_not_present_lacks_coverage_fields():
    payload = {
        "dimensions": [
            {
                "dimension_id": "behavioral-intervention",
                "dimension_name": "Behavioral Intervention",
                "present": False,
                "presence_reason": "Does not apply.",
                # No `covered`, `coverage_evidence`, `materiality_note`
            },
        ],
    }
    parsed = _parse_dimension_detection(payload)
    assert len(parsed) == 1
    d = parsed[0]
    assert d.present is False
    assert d.covered is False
    assert d.coverage_evidence == ""
    assert d.materiality_note == ""
    assert d.presence_reason == "Does not apply."


def test_max_gaps_cap_only_counts_present_and_uncovered():
    """Non-detected dimensions must NOT be counted against _MAX_GAPS=5.

    Pre-PR, every entry in the parsed list was assumed detected. With non-
    detected dimensions now in the list, the cap must filter on
    `present AND not covered` — otherwise the safety net triggers
    spuriously and demotes legitimate gaps to covered.
    """
    payload_dims = []
    # 6 present-and-uncovered (one over the cap)
    for i in range(6):
        payload_dims.append({
            "dimension_id": f"gap-dim-{i}",
            "dimension_name": f"Gap {i}",
            "present": True,
            "covered": False,
            "coverage_evidence": "missing",
            "materiality_note": f"material reason {i}",
            "presence_reason": "",
        })
    # 5 present-and-covered (must not change)
    for i in range(5):
        payload_dims.append({
            "dimension_id": f"covered-dim-{i}",
            "dimension_name": f"Covered {i}",
            "present": True,
            "covered": True,
            "coverage_evidence": "addressed",
            "materiality_note": "",
            "presence_reason": "",
        })
    # 4 not-present (must not contribute to gap count)
    for i in range(4):
        payload_dims.append({
            "dimension_id": f"absent-dim-{i}",
            "dimension_name": f"Absent {i}",
            "present": False,
            "presence_reason": f"not relevant {i}",
        })

    parsed = _parse_dimension_detection({"dimensions": payload_dims})

    # All 15 entries persist
    assert len(parsed) == 15

    # Exactly _MAX_GAPS gaps survive (sixth demoted by the cap)
    actual_gaps = [d for d in parsed if d.present and not d.covered]
    assert len(actual_gaps) == _MAX_GAPS, (
        f"Cap should demote 6 → {_MAX_GAPS}; got {len(actual_gaps)}"
    )

    # Not-present dimensions remain not-present (untouched by the cap demotion)
    not_present = [d for d in parsed if not d.present]
    assert len(not_present) == 4
    for d in not_present:
        assert d.presence_reason.startswith("not relevant")


def test_parser_backwards_compatible_with_old_payload_shape():
    """Old payloads (no `present` field) must default to present=True.

    Legacy archived result.json files predate the new shape; re-loading them
    via from_payload / re-parsing must not crash and must produce sensible
    DetectedDimension records (every entry treated as detected).
    """
    payload = {
        "dimensions": [
            {
                "dimension_id": "incentive-alignment",
                "dimension_name": "Incentive Alignment",
                "covered": False,
                "coverage_evidence": "missing",
                "materiality_note": "important",
            },
            {
                "dimension_id": "stakeholder-alignment",
                "dimension_name": "Stakeholder Alignment",
                "covered": True,
                "coverage_evidence": "addressed",
                "materiality_note": "",
            },
        ],
    }
    parsed = _parse_dimension_detection(payload)
    assert len(parsed) == 2
    for d in parsed:
        assert d.present is True
        assert d.presence_reason == ""


def test_to_payload_round_trips_present_and_presence_reason():
    """The card serializer must persist present + presence_reason so they
    land in audit_summary.dimensions[*].
    """
    from engine.system_b.structural_coverage import StructuralCoverageCard

    parsed = _parse_dimension_detection(_new_shape_payload())
    card = StructuralCoverageCard(question_type="decision-evaluation", dimensions=parsed)
    payload = card.to_payload()

    by_id = {d["dimension_id"]: d for d in payload["dimensions"]}
    assert by_id["behavioral-intervention"]["present"] is False
    assert by_id["behavioral-intervention"]["presence_reason"].startswith("No behavior change")
    assert by_id["incentive-alignment"]["present"] is True
    assert by_id["incentive-alignment"]["presence_reason"] == ""

    # Round-trip via from_payload — fields preserved
    restored = StructuralCoverageCard.from_payload(payload)
    by_id2 = {d.dimension_id: d for d in restored.dimensions}
    assert by_id2["behavioral-intervention"].present is False
    assert by_id2["behavioral-intervention"].presence_reason.startswith("No behavior change")
    assert by_id2["incentive-alignment"].present is True
