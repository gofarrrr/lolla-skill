"""PR 2 Fix #3 — track candidates silently omitted by verifier.

In the consultant case the audit memo investigated, ``cognitive-dissonance``
was sent as one of 60 candidates but never appeared in the verifier's
response — neither accepted nor rejected. ``parse_verification_response``
walks the LLM's accepted/rejected arrays only; candidates the LLM
silently drops disappear from the audit trail entirely. The fix is to
reconcile the candidate set against the union of mentioned ids and
surface the remainder as a fourth bucket with
``drop_reason: "not_in_verifier_response"``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.companion_routing import parse_verification_response


def test_silently_omitted_surfaces_when_candidate_missing_from_response():
    raw = {
        "accepted": [
            {
                "model_id": "checklists",
                "presence_mode": "executed",
                "evidence_quote": "we ran through the checklist",
                "presence_explanation": "the answer applied a structured checklist",
            }
        ],
        "rejected": [
            {"model_id": "second-order-thinking", "rejection_reason": "too generic"},
        ],
    }
    answer = "we ran through the checklist before deciding"

    accepted, rejected, quote_repairs, silently_omitted = parse_verification_response(
        raw,
        vanilla_answer=answer,
        candidate_ids={"checklists", "second-order-thinking", "cognitive-dissonance"},
    )

    assert {a["model_id"] for a in accepted} == {"checklists"}
    assert {r["model_id"] for r in rejected} == {"second-order-thinking"}
    assert quote_repairs == []
    assert len(silently_omitted) == 1
    assert silently_omitted[0]["model_id"] == "cognitive-dissonance"
    assert silently_omitted[0]["drop_reason"] == "not_in_verifier_response"


def test_silently_omitted_empty_when_all_candidates_mentioned():
    """Existing 3-bucket behaviour preserved when no candidate is omitted."""
    raw = {
        "accepted": [
            {
                "model_id": "checklists",
                "presence_mode": "executed",
                "evidence_quote": "we ran through the checklist",
                "presence_explanation": "structured execution",
            }
        ],
        "rejected": [
            {"model_id": "second-order-thinking", "rejection_reason": "too generic"},
        ],
    }
    answer = "we ran through the checklist"

    accepted, rejected, _quote_repairs, silently_omitted = parse_verification_response(
        raw,
        vanilla_answer=answer,
        candidate_ids={"checklists", "second-order-thinking"},
    )

    assert silently_omitted == []
    assert {a["model_id"] for a in accepted} == {"checklists"}
    assert {r["model_id"] for r in rejected} == {"second-order-thinking"}


def test_silently_omitted_reproduces_consultant_60_to_59_shape():
    """60 candidates in, 59 mentioned, exactly 1 silently omitted — the consultant case shape."""
    candidate_ids = {f"model-{i:02d}" for i in range(60)}
    # The verifier 'mentions' 59 of them — model-42 is the ghost
    raw = {
        "accepted": [
            {
                "model_id": f"model-{i:02d}",
                "presence_mode": "executed",
                "evidence_quote": "executed mechanism quote",
                "presence_explanation": "applies",
            }
            for i in range(4)
        ],
        "rejected": [
            {"model_id": f"model-{i:02d}", "rejection_reason": "mechanism absent"}
            for i in range(4, 60) if i != 42
        ],
    }
    answer = "executed mechanism quote in the answer"

    _, _, _, silently_omitted = parse_verification_response(
        raw,
        vanilla_answer=answer,
        candidate_ids=candidate_ids,
    )

    assert len(silently_omitted) == 1
    assert silently_omitted[0]["model_id"] == "model-42"
    assert silently_omitted[0]["drop_reason"] == "not_in_verifier_response"
