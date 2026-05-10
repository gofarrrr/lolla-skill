"""Tests for memo rendering from result JSON."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.render_memo import render_memo


MINIMAL_RESULT = {
    "extraction": {
        "decision_situation": "Should I grant 15% equity to Marcus? He built most of the platform.",
        "turns": [
            {
                "turn_index": 1,
                "speaker": "user",
                "text": "Should I grant 15% equity to Marcus? He built most of the platform.",
            },
            {
                "turn_index": 1,
                "speaker": "assistant",
                "text": "Yes, granting equity seems reasonable given his contributions.",
            },
        ],
    },
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


NEW_MEMO_RESULT = {
    **FULL_RESULT,
    "memo_substantive_title": "The equity decision turned on an untested future contribution",
    "memo_orientation_note": (
        "You were not deciding whether Marcus mattered. You had already crossed that line. "
        "The live question was whether a 15% grant priced the future partnership or simply rewarded the past build.\n\n"
        "My original answer leaned toward a phased equity approach, but the weak point was the threshold: "
        "I treated past platform contribution as if it settled future dependence. The revised advice is narrower. "
        "Test what Marcus will own, what changes if he leaves, and what other engineers will read into the grant before turning the number into a commitment."
    ),
    "memo_what_changed": (
        "### Test future dependence before pricing equity\n\n"
        "The advice now asks whether Marcus remains the bottleneck after the current platform build, not whether he earned gratitude for past work."
    ),
    "memo_what_still_holds": (
        "- Marcus's contribution is real.\n"
        "- A phased structure still beats a clean yes/no grant."
    ),
    "memo_take_back_or_set_aside": (
        "I would take back the confidence of the first number. The direction can survive; the precision cannot."
    ),
    "memo_pressure_check": (
        "One more point: the other engineers are not background noise. Their reaction changes the cost of any special grant."
    ),
}


def _decision_note_layer(output: str) -> str:
    for heading in ("## Appendix: Audit trace", "## Appendix: Additional unresolved questions"):
        if heading in output:
            return output.split(heading, 1)[0]
    return output


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
    output = render_memo(result, include_audit_appendix=True)
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
    """Minimal result with only extraction + detected_tendencies produces valid memo."""
    output = render_memo(MINIMAL_RESULT)
    assert output.startswith("# ")


def test_new_memo_shape_starts_with_substantive_title():
    """New memo fields switch renderer to decision-note shape."""
    output = render_memo(NEW_MEMO_RESULT)
    assert output.startswith("# The equity decision turned on an untested future contribution")
    assert "# Reasoning Audit:" not in output
    assert "You were not deciding whether Marcus mattered" in output


def test_new_memo_shape_is_product_clean_by_default():
    """Decision-note memos omit the deterministic audit trace by default."""
    output = render_memo(NEW_MEMO_RESULT)
    assert "## What changed in the advice" in output
    assert "## Appendix: Audit trace" not in output
    assert "### Challenge points" not in output
    assert "### Model connections" not in output
    assert "Inversion" not in output
    assert "Second-Order Thinking" not in output


def test_new_memo_can_include_audit_trace_when_requested():
    """Operators can still render the full deterministic audit trace explicitly."""
    output = render_memo(NEW_MEMO_RESULT, include_audit_appendix=True)
    assert "## Appendix: Audit trace" in output
    assert output.index("## What changed in the advice") < output.index("## Appendix: Audit trace")
    assert "### Challenge points" in output
    assert "### Model connections" in output
    assert output.index("### Challenge points") > output.index("## Appendix: Audit trace")


def test_new_memo_questions_replace_structural_gaps_section():
    """Structural gaps become user-answerable questions in the main body."""
    output = render_memo(NEW_MEMO_RESULT)
    assert "## Questions still unanswered" in output
    assert "How would other engineers react" in output
    assert "## Structural Gaps" not in output


def test_new_memo_questions_are_capped_in_decision_note_with_remainder_in_appendix():
    """The decision note should not become a structural-gaps backlog."""
    result = {
        **NEW_MEMO_RESULT,
        "structural_coverage_card": {
            "gap_questions": [
                {"questions": ["Question one?", "Question two?"]},
                {"questions": ["Question three?", "Question four?", "Question five?"]},
            ],
        },
    }

    output = render_memo(result)
    decision_questions = output.split("## Appendix: Additional unresolved questions", 1)[0].split(
        "## Questions still unanswered", 1
    )[1]
    appendix = output.split("## Appendix: Additional unresolved questions", 1)[1]

    assert "Question one?" in decision_questions
    assert "Question two?" in decision_questions
    assert "Question three?" in decision_questions
    assert "Question four?" not in decision_questions
    assert "2 more unresolved question(s)" in decision_questions
    assert "Question four?" in appendix
    assert "Question five?" in appendix


def test_new_memo_omits_empty_pressure_check_section():
    """No empty pressure-check heading when no memo divergence survives."""
    result = {**NEW_MEMO_RESULT, "memo_pressure_check": ""}
    output = render_memo(result, include_audit_appendix=True)
    assert "## One more pressure check" not in output


def test_new_memo_decision_note_layer_has_no_machinery_terms():
    """Decision-note layer avoids internal product machinery terms."""
    output = render_memo(NEW_MEMO_RESULT)
    layer = _decision_note_layer(output)
    banned = [
        "Beat",
        "Step",
        "Lane",
        "sub-agent",
        "DeltaCard",
        "CompanionCheatSheet",
        "FramePressureCard",
        "StructuralCoverageCard",
        "pipeline",
        "independent review",
        "isolated review",
        "reviewers",
        "V60",
        "affordance",
        "chunk",
        "packet",
        "ledger",
    ]
    for term in banned:
        assert term not in layer


def test_new_memo_strips_operator_attribution_line_from_pressure_check():
    """Memo pressure checks should present the argument, not the hidden source."""
    result = {
        **NEW_MEMO_RESULT,
        "memo_pressure_check": (
            "Two additional angles survived independent review.\n\n"
            "First: the pass bar should scale with reversibility."
        ),
    }

    output = render_memo(result)

    assert "independent review" not in output
    assert "Two additional angles survived" not in output
    assert "First: the pass bar should scale with reversibility" in output


def test_new_memo_appendix_cleans_machine_shaped_challenge_wrappers():
    """Raw challenge wrappers should not make the appendix read like JSON plumbing."""
    result = {
        **NEW_MEMO_RESULT,
        "delta_card": {
            "findings": [
                {
                    "tendency_name": "Social-Proof Tendency",
                    "severity": "medium",
                    "specific_passage": "USER [Turn 5]: 'Everyone does this.' ASSISTANT [Turn 5]: 'Then it is not differentiating.'",
                    "challenge_statement": (
                        "Social-Proof: challenge 'USER [Turn 5]: "
                        "'Everyone does this.' ASSISTANT [Turn 5]: "
                        "'Then it is not differentiating.'' because the answer "
                        "used visible consensus as evidence without checking whether the pool was self-selecting"
                    ),
                },
            ],
        },
    }

    output = render_memo(result, include_audit_appendix=True)

    assert "Social-Proof: challenge" not in output
    assert "used visible consensus as evidence" in output
    assert " ...\n" not in output


def test_new_memo_can_parse_revised_answer_sections_when_fields_missing():
    """Renderer falls back to revised_answer sections for partial memo fields."""
    result = {
        **FULL_RESULT,
        "memo_substantive_title": "The equity answer needs a narrower test",
        "memo_orientation_note": "The memo opens with the decision tension and the changed advice.",
        "memo_what_changed": "",
        "memo_what_still_holds": "",
        "memo_take_back_or_set_aside": "",
        "revised_answer": (
            "## Updated position\n\n"
            "§1 What survived\n\n"
            "The phased structure still holds.\n\n"
            "§2 What I'd take back\n\n"
            "The first number was too confident.\n\n"
            "§3 What actually shifted\n\n"
            "Ask what Marcus owns after the next platform milestone."
        ),
    }
    output = render_memo(result)
    assert "## What changed in the advice" in output
    assert "Ask what Marcus owns" in output
    assert "## What still holds" in output
    assert "The phased structure still holds" in output
    assert "## What I'd take back or set aside" in output
    assert "The first number was too confident" in output
    # Should not contain any optional sections
    assert "## Key Findings" not in output
    assert "## Mental Model Connections" not in output
    assert "## Frame Alternatives" not in output
    assert "## Structural Gaps" not in output
    assert "## Delivery Check" not in output
    assert "## Updated Position" not in output
    assert "## Pressure Check" not in output
