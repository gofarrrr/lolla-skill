"""Tests for the case-learning HTML artifact renderer."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.render_case_learning_html import render_case_learning_html


HTML_RESULT = {
    "status": "ok",
    "extraction": {
        "decision_situation": "Should I grant 15% equity to Marcus after he built most of the platform?",
        "turns": [
            {
                "speaker": "user",
                "text": "Should I grant 15% equity to Marcus after he built most of the platform?",
            }
        ],
    },
    "memo_substantive_title": "The equity decision turned on an untested future contribution",
    "memo_orientation_note": (
        "You were not deciding whether Marcus mattered. The live question was whether the grant "
        "priced the future partnership or simply rewarded the past build."
    ),
    "memo_what_changed": (
        "**Test future dependence before pricing equity.** The advice now asks whether Marcus "
        "remains the bottleneck after the current platform build.\n\n"
        "**Separate gratitude from governance.** The grant should be staged around future ownership, "
        "not only past contribution."
    ),
    "memo_what_still_holds": "- Marcus's contribution is real.",
    "memo_take_back_or_set_aside": "The first number was too confident.",
    "memo_pressure_check": "Other engineers are not background noise.",
    "companion_cheat_sheet": {
        "anchors": [
            {
                "model_id": "inversion",
                "display_name": "Inversion",
                "presence_explanation": "The advice improved once it asked what would make the grant fail.",
                "evidence_quote": "What if Marcus leaves after the next platform milestone?",
                "chunks": [
                    {
                        "chunk_type": "identity",
                        "text": "Select when: You need to test a plan by asking what would make it fail. | Danger when: Used as generic pessimism.",
                    },
                    {"chunk_type": "premortem", "text": "What would make this decision fail even if the first step works?"},
                    {"chunk_type": "failure_mode", "text": "Inversion fails when it becomes abstract pessimism instead of concrete failure search."},
                ],
            },
            {
                "model_id": "second-order-thinking",
                "display_name": "Second-Order Thinking",
                "presence_explanation": "The grant changes how other engineers interpret future rewards.",
                "chunks": [
                    {"chunk_type": "heuristic", "text": "Ask what incentives the decision creates next."},
                    {"chunk_type": "premortem", "text": "What behavior does this reward teach the team?"},
                ],
            },
        ]
    },
    "frame_pressure_card": {
        "reframings": [
            {
                "reframed_question": "What equity structure would still be fair if Marcus left in two years?",
                "what_opens": "Tests whether the number is a retention instrument or a reward for sunk effort.",
                "grounding_model": "inversion",
            }
        ]
    },
    "structural_coverage_card": {
        "gap_questions": [
            {
                "dimension_name": "Stakeholder Alignment",
                "questions": [
                    "How would other engineers react to this grant?",
                    "What explanation would make the grant feel procedurally fair?",
                ],
            }
        ]
    },
    "gap_check": {
        "lanes": [
            {"lane_name": "CompanionCheatSheet", "status": "completed", "divergences": [{"description": "test"}]},
            {"lane_name": "StructuralCoverageCard", "status": "completed", "divergences": []},
        ]
    },
    "run_health": {
        "overall": "healthy",
        "capture": "good",
        "substrate": "ok",
        "product_output_health": "clean",
        "issues": [],
        "v60_consideration_ledger": "valid",
        "v60_selected_chunk_count": 4,
        "v60_consideration_disposition_counts": {"used": 2, "rejected": 1, "deferred": 1},
    },
    "usage_summary": {"estimated_total_cost_usd": 0.1234, "total_calls": 12},
    "v60_enrichment": {"status": "active"},
}


def test_case_learning_html_has_decision_opening_and_learning_sections():
    output = render_case_learning_html(HTML_RESULT)

    assert output.startswith("<!doctype html>")
    assert "The equity decision turned on an untested future contribution" in output
    assert "What Changed" in output
    assert "What This Case Teaches" in output
    assert "Mental Models Worth Learning" in output
    assert "Questions Still Open" in output
    assert "Technical trace" in output


def test_case_learning_html_renders_model_cards_as_educational_units():
    output = render_case_learning_html(HTML_RESULT)

    assert "Inversion" in output
    assert "You need to test a plan by asking what would make it fail" in output
    assert "What would make this decision fail even if the first step works?" in output
    assert "Inversion fails when it becomes abstract pessimism" in output
    assert "What equity structure would still be fair" in output


def test_case_learning_html_keeps_process_detail_collapsed():
    output = render_case_learning_html(HTML_RESULT)
    before_trace = output.split('<section class="section trace"', 1)[0]

    assert "CompanionCheatSheet" not in before_trace
    assert "StructuralCoverageCard" not in before_trace
    assert "ledger" not in before_trace.lower()
    assert "Private enrichment" in output
    assert "CompanionCheatSheet" in output
    assert "<td>0</td>" in output


def test_case_learning_html_escapes_user_controlled_content():
    result = {
        **HTML_RESULT,
        "memo_substantive_title": "Bad <script>alert('x')</script> title",
        "memo_orientation_note": "Contains <img src=x onerror=alert(1)> markup.",
        "companion_cheat_sheet": {
            "anchors": [
                {
                    "display_name": "<b>Injected</b>",
                    "presence_explanation": "Use <script>bad()</script>.",
                    "chunks": [],
                }
            ]
        },
    }

    output = render_case_learning_html(result)

    assert "<script>alert('x')</script>" not in output
    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in output
    assert "<img src=x" not in output
    assert "&lt;b&gt;Injected&lt;/b&gt;" in output
