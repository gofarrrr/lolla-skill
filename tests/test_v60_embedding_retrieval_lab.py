from __future__ import annotations

import numpy as np

from scripts.run_v60_embedding_retrieval_lab import (
    build_v60_chunks,
    cosine_scores,
    hybrid_rrf_rank,
    reserved_novelty_rank,
)


def test_build_v60_chunks_includes_affordances_and_absences() -> None:
    payload = {
        "affordances": [
            {
                "model_id": "optionality",
                "affordance_id": "optionality.expand-before-evaluating",
                "name": "Expand before evaluating",
                "status": "supported",
                "confidence": "high",
                "mechanism": "Open the option set before committing.",
                "activation_shape": {
                    "use_when": ["A choice is framed too narrowly."],
                    "case_evidence_needed": ["The current option set."],
                    "do_not_use_when": ["The decision is already constrained."],
                },
                "diagnostic_questions": ["What third option exists?"],
                "misuse_guards": ["Do not create fake options."],
                "source_evidence": [{"source_quote": "expand the set"}],
            }
        ],
        "absence_records": [
            {
                "model_id": "optionality",
                "attempted_field": "infinite-option-generation",
                "status": "not_supported_by_source",
                "runtime_policy": "do_not_promote",
                "reason": "The source does not support endless option generation.",
                "source_evidence": [{"source_quote": "not endless"}],
            }
        ],
    }

    chunks = build_v60_chunks(payload)

    assert [chunk.chunk_kind for chunk in chunks] == ["affordance", "absence"]
    assert chunks[0].chunk_id == "aff::optionality.expand-before-evaluating"
    assert chunks[1].chunk_id == "abs::optionality::infinite-option-generation"
    assert "Open the option set" in chunks[0].text
    assert "do_not_promote" in chunks[1].text


def test_cosine_scores_orders_matching_vectors() -> None:
    matrix = np.asarray([[1.0, 0.0], [0.0, 1.0], [0.7, 0.7]], dtype=np.float32)
    query = np.asarray([1.0, 0.0], dtype=np.float32)

    scores = cosine_scores(matrix, query)

    assert scores[0] > scores[2] > scores[1]


def test_hybrid_rrf_rank_prefers_models_seen_by_both_rankers() -> None:
    lane_rank = ["a", "b", "c", "d"]
    embedding_rank = ["x", "b", "y", "a"]

    ranked = hybrid_rrf_rank(lane_rank, embedding_rank)

    assert ranked.index("b") < ranked.index("c")
    assert ranked.index("a") < ranked.index("x")


def test_reserved_novelty_keeps_lane_prefix_then_adds_embedding_novelty() -> None:
    ranked = reserved_novelty_rank(
        lane_selected=["a", "b", "c", "d", "e", "f"],
        embedding_rank=["b", "x", "y", "a", "z"],
        card_cap=8,
        lane_slots=5,
    )

    assert ranked == ["a", "b", "c", "d", "e", "x", "y", "z"]
