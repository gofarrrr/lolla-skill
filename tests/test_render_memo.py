"""Tests for memo rendering from result JSON."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.render_memo import render_memo


MINIMAL_RESULT = {
    "query": "Should I grant 15% equity to Marcus? He built most of the platform.",
    "vanilla_answer": "Yes, granting equity seems reasonable given his contributions.",
    "detected_tendencies": [],
}

FULL_RESULT = {
    **MINIMAL_RESULT,
    "delta_card": {
        "findings": [
            {
                "tendency_name": "Overoptimism",
                "severity": "high",
                "specific_passage": "Marcus built most of the platform",
                "challenge_statement": "You assumed future contributions will match past ones.",
            },
            {
                "tendency_name": "Anchoring",
                "severity": "medium",
                "specific_passage": "15% seems right",
                "challenge_statement": "The 15% figure anchored subsequent reasoning.",
            },
            {
                "tendency_name": "Sunk Cost",
                "severity": "low",
                "specific_passage": "He already invested years",
                "challenge_statement": "Past investment shouldn't drive future equity.",
            },
        ],
    },
    "companion_cheat_sheet": {
        "anchors": [
            {
                "display_name": "Inversion",
                "presence_mode": "corrective",
                "presence_explanation": "Ask what would make this equity grant fail.",
                "evidence_quote": "built most of the platform",
            },
            {
                "display_name": "Second-Order Thinking",
                "presence_mode": "exploratory",
                "presence_explanation": "Consider downstream effects on other employees.",
            },
        ],
    },
    "frame_pressure_card": {
        "reframings": [
            {
                "reframed_question": "What would a fair equity structure look like if Marcus left in 2 years?",
                "what_opens": "Tests whether equity is retention or reward.",
                "reframe_move_type": "inversion",
                "grounding_model": "inversion",
            },
        ],
    },
    "structural_coverage_card": {
        "gap_questions": [
            {
                "dimension_id": "stakeholder",
                "dimension_name": "Stakeholder Impact",
                "questions": ["How would other engineers react to this equity grant?"],
            },
            {
                "dimension_id": "temporal",
                "dimension_name": "Temporal Horizon",
                "questions": ["What happens to this equity if the company pivots?"],
            },
        ],
        "gap_routes": [
            {"dimension_id": "stakeholder", "model_ids": ["second-order-thinking"]},
            {"dimension_id": "temporal", "model_ids": ["inversion"]},
        ],
    },
    "bullshit_profile": {
        "summary": {
            "total_passages": 10,
            "passages_with_detections": 5,
            "total_clear": 32,
            "total_marginal": 3,
        },
        "passages": [
            {"passage": "test", "detections": [{"subtype": "unverified_claims", "severity": "clear"}] * 20},
            {"passage": "test2", "detections": [{"subtype": "vague_claims", "severity": "clear"}] * 12},
        ],
    },
    "revised_answer": "After considering the structural patterns, I'd recommend a phased equity approach.",
    "gap_check": {
        "lanes": [
            {"lane_name": "DeltaCard", "divergences": []},
            {"lane_name": "CompanionCheatSheet", "divergences": [
                {"finding": "Inversion model was underweighted", "explanation": "The corrective model deserved more emphasis."},
            ]},
            {"lane_name": "FramePressureCard", "divergences": [
                {"finding": "Temporal reframing missing", "explanation": "Time horizon question was not explored."},
            ]},
            {"lane_name": "StructuralCoverageCard", "divergences": []},
        ],
    },
}


def test_memo_starts_with_heading_and_contains_query():
    """Memo starts with a markdown heading and contains the decision situation."""
    output = render_memo(MINIMAL_RESULT)
    assert output.startswith("# ")
    assert "equity" in output.lower()


def test_findings_section_present():
    """Memo contains Key Findings section with entries sorted by severity."""
    output = render_memo(FULL_RESULT)
    assert "## Key Findings" in output
    assert "Overoptimism" in output
    assert "challenge_statement" not in output  # no raw field names
    # High severity should appear before medium
    high_pos = output.index("Overoptimism")
    medium_pos = output.index("Anchoring")
    assert high_pos < medium_pos


def test_findings_include_challenge_statement():
    """Each finding includes its challenge statement text."""
    output = render_memo(FULL_RESULT)
    assert "You assumed future contributions will match past ones" in output


def test_companion_section_present():
    """Memo contains Mental Model Connections section."""
    output = render_memo(FULL_RESULT)
    assert "## Mental Model Connections" in output
    assert "Inversion" in output
    assert "Ask what would make this equity grant fail" in output
    assert "Second-Order Thinking" in output


def test_frame_alternatives_section_present():
    """Memo contains Frame Alternatives section with reframings."""
    output = render_memo(FULL_RESULT)
    assert "## Frame Alternatives" in output
    assert "What would a fair equity structure look like" in output
    assert "Tests whether equity is retention or reward" in output


def test_structural_gaps_section_present():
    """Memo contains Structural Gaps section."""
    output = render_memo(FULL_RESULT)
    assert "## Structural Gaps" in output
    assert "Stakeholder Impact" in output
    assert "How would other engineers react" in output


def test_delivery_check_present_when_detections():
    """Memo contains Delivery Check when total_clear > 0."""
    output = render_memo(FULL_RESULT)
    assert "## Delivery Check" in output
    assert "32" in output


def test_delivery_check_absent_when_zero():
    """Delivery Check section absent when total_clear == 0."""
    result = {
        **FULL_RESULT,
        "bullshit_profile": {
            "summary": {"total_passages": 10, "passages_with_detections": 0, "total_clear": 0, "total_marginal": 0},
            "passages": [],
        },
    }
    output = render_memo(result)
    assert "## Delivery Check" not in output


def test_updated_position_present():
    """Memo contains Updated Position section with revised_answer."""
    output = render_memo(FULL_RESULT)
    assert "## Updated Position" in output
    assert "phased equity approach" in output


def test_updated_position_absent_when_null():
    """Updated Position section absent when revised_answer is null."""
    result = {**FULL_RESULT, "revised_answer": None}
    output = render_memo(result)
    assert "## Updated Position" not in output


def test_pressure_check_present():
    """Memo contains Pressure Check section listing divergent lanes."""
    output = render_memo(FULL_RESULT)
    assert "## Pressure Check" in output
    assert "Mental Model Review" in output
    assert "Inversion model was underweighted" in output
    # DeltaCard has 0 divergences — should not appear
    pc_section = output.split("## Pressure Check")[1]
    assert "Structural Findings" not in pc_section
    # Card names should never appear
    assert "CompanionCheatSheet" not in pc_section
    assert "DeltaCard" not in pc_section


def test_duplicate_passage_rendered_once():
    """When two findings share the same specific_passage, the blockquote appears only once."""
    shared_passage = "Grant Marcus partnership via equity with 15% vesting over 4 years"
    result = {
        **MINIMAL_RESULT,
        "delta_card": {
            "findings": [
                {
                    "tendency_name": "Inconsistency-Avoidance",
                    "severity": "high",
                    "specific_passage": shared_passage,
                    "challenge_statement": "Challenge A",
                },
                {
                    "tendency_name": "Overoptimism",
                    "severity": "medium",
                    "specific_passage": shared_passage,
                    "challenge_statement": "Challenge B",
                },
            ],
        },
    }
    output = render_memo(result)
    # Both findings should appear
    assert "Inconsistency-Avoidance" in output
    assert "Overoptimism" in output
    # Both challenges should appear
    assert "Challenge A" in output
    assert "Challenge B" in output
    # The passage blockquote should appear only once
    assert output.count(f"> {shared_passage}") == 1


def test_minimal_result_no_errors():
    """Minimal result with only query/vanilla_answer/detected_tendencies produces valid memo."""
    output = render_memo(MINIMAL_RESULT)
    assert output.startswith("# ")
    # Should not contain any optional sections
    assert "## Key Findings" not in output
    assert "## Mental Model Connections" not in output
    assert "## Frame Alternatives" not in output
    assert "## Structural Gaps" not in output
    assert "## Delivery Check" not in output
    assert "## Updated Position" not in output
    assert "## Pressure Check" not in output
