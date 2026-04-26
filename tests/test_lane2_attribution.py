"""Tests for the Lane 2 attribution surfaces added in
fix/lane2-variance-attribution-2026-04-26.

Covers:
- recall_candidates emits per-source rank metadata (keyword_rank,
  embedding_rank, final_rank, recall_source ∈ {keyword, embedding, both}).
- run_verification_call_from_packet returns the 4-tuple (detected,
  rejected, accepted_before_cap, capped_models) and the cap enforcement
  surfaces capped models — separately from rejected.
- companion_candidate_cap config flows from PipelineConfig through to
  recall_candidates.

No real LLM calls. All boundary clients are mocked.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.companion import FingerprintPayload
from engine.system_b.companion_routing import (
    _DETECTED_MODELS_CAP,
    recall_candidates,
    run_verification_call_from_packet,
)
from engine.system_b.conversation_context import (
    ConversationContext,
    ExtractionPayload,
    Turn,
)
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.packet_builders.lane4 import build_lane4_packet
from engine.system_b.pipeline import PipelineConfig, SystemBPipeline


# ---------- recall_candidates per-source rank tracking ----------


def _kg(model_ids: list[str]) -> dict:
    """Minimal knowledge graph: each model has a display_name + a
    select_when keyword that matches the test assistant_text."""
    models = {}
    for mid in model_ids:
        models[mid] = {
            "display_name": mid.replace("-", " ").title(),
            "select_when": [mid.replace("-", " ")],
        }
    return {"models": models}


def test_recall_candidates_keyword_path_tags_recall_source_and_rank():
    kg = _kg(["opportunity-cost", "second-order-thinking"])
    fp = FingerprintPayload(raw=[], validated=[], dropped=[])
    text = "weighing opportunity cost and second order thinking"
    candidates = recall_candidates(
        assistant_text=text,
        fingerprint_payload=fp,
        knowledge_graph=kg,
        reasoning_signals={},
    )
    assert len(candidates) == 2
    by_id = {c["model_id"]: c for c in candidates}
    for c in candidates:
        assert c["recall_source"] == "keyword"
        assert isinstance(c["keyword_rank"], int) and c["keyword_rank"] >= 1
        assert c["embedding_rank"] is None
        assert isinstance(c["final_rank"], int) and c["final_rank"] >= 1
    # final_rank is 1-indexed and dense
    final_ranks = sorted(c["final_rank"] for c in candidates)
    assert final_ranks == [1, 2]


def test_recall_candidates_max_candidates_caps_results():
    """The max_candidates kwarg must cap the returned list size."""
    kg = _kg([f"model-{i}" for i in range(50)])
    fp = FingerprintPayload(raw=[], validated=[], dropped=[])
    # Text matches every model name.
    text = " ".join(f"model {i}" for i in range(50))
    candidates = recall_candidates(
        assistant_text=text,
        fingerprint_payload=fp,
        knowledge_graph=kg,
        reasoning_signals={},
        max_candidates=10,
    )
    assert len(candidates) == 10
    # final_rank is 1..10
    assert sorted(c["final_rank"] for c in candidates) == list(range(1, 11))


def test_recall_skips_embedding_when_cap_filled_by_keyword():
    """Measurement contract: when primary keyword recall fills max_candidates,
    the embedding path MUST NOT run.

    Pins three guarantees the 24-run attribution campaign depends on:

    1. ``rank_models_expanded`` is never called → no untraced
       embedding/expansion cost is paid.
    2. No returned candidate carries ``recall_source="both"`` → the
       diagnostic metric does not falsely imply embedding contributed when
       it was structurally prevented from doing so.
    3. Returned candidates still carry dense, 1-indexed ``final_rank``
       values → the audit shape is identical to the cap-not-yet-full case.

    Whether embedding *should* be allowed to displace low-rank keyword
    candidates in this case is an explicit open question deferred to the
    post-attribution fix PR.
    """
    # 5 keyword-matching models + cap=5 → primary keyword fills the cap.
    kg = _kg([f"model-{i}" for i in range(5)])
    fp = FingerprintPayload(raw=[], validated=[], dropped=[])
    text = " ".join(f"model {i}" for i in range(5))

    rank_calls: list[tuple] = []

    class FakeRetriever:
        def rank_models_expanded(self, query_text, api_key, top_k):
            rank_calls.append((query_text[:30], api_key, top_k))
            return [{"model_id": "extra-model", "score": 0.9}]

    candidates = recall_candidates(
        assistant_text=text,
        fingerprint_payload=fp,
        knowledge_graph=kg,
        reasoning_signals={},
        max_candidates=5,
        embedding_retriever=FakeRetriever(),
        embedding_api_key="fake-key",
    )

    # (1) Embedding path was not invoked.
    assert rank_calls == [], (
        "rank_models_expanded must NOT be called when keyword recall already "
        "filled max_candidates — would pay untraced cost on cap-saturated runs"
    )
    # (2) No 'both' tag leakage from a never-ran embedding path.
    assert all(c["recall_source"] == "keyword" for c in candidates), (
        "recall_source must stay 'keyword' across all candidates when embedding "
        "never ran; 'both' would falsely imply embedding contributed"
    )
    # (3) final_rank is dense and 1-indexed regardless of cap-saturation path.
    assert sorted(c["final_rank"] for c in candidates) == [1, 2, 3, 4, 5]


def test_recall_candidates_embedding_path_tags_both_when_overlapping():
    """When embedding recall surfaces a model already found by keyword recall,
    recall_source is promoted to 'both' and embedding_rank is set."""
    kg = _kg(["opportunity-cost", "inversion"])
    fp = FingerprintPayload(raw=[], validated=[], dropped=[])

    class FakeRetriever:
        def rank_models_expanded(self, query_text, api_key, top_k):
            return [
                {"model_id": "opportunity-cost", "score": 0.9},
                {"model_id": "endowment-effect", "score": 0.8},  # not in kg, dropped
                {"model_id": "inversion", "score": 0.7},
            ]

    candidates = recall_candidates(
        assistant_text="opportunity cost reasoning",
        fingerprint_payload=fp,
        knowledge_graph=kg,
        reasoning_signals={},
        embedding_retriever=FakeRetriever(),
        embedding_api_key="fake-key",
    )
    by_id = {c["model_id"]: c for c in candidates}
    # opportunity-cost: keyword-found, then embedding overlap -> "both"
    assert by_id["opportunity-cost"]["recall_source"] == "both"
    assert by_id["opportunity-cost"]["embedding_rank"] == 1
    assert isinstance(by_id["opportunity-cost"]["keyword_rank"], int)
    # inversion: not surfaced by keyword (text doesn't contain it), found by embedding
    assert by_id["inversion"]["recall_source"] == "embedding"
    assert by_id["inversion"]["keyword_rank"] is None
    assert by_id["inversion"]["embedding_rank"] == 3


# ---------- run_verification_call_from_packet 4-tuple shape + cap ----------


def _ctx(assistant_text: str) -> ConversationContext:
    return ConversationContext(
        turns=(
            Turn(turn_index=1, speaker="user", text="placeholder user turn"),
            Turn(turn_index=1, speaker="assistant", text=assistant_text),
        ),
        extraction=ExtractionPayload(
            decision_situation="x",
            live_constraints=(),
            synthesized_position="",
            reasoning_passages=(),
            original_framing="",
            dropped_threads=(),
        ),
    )


def _packet(assistant_text: str):
    return build_lane4_packet(construct_conversation_ir(_ctx(assistant_text)))


class _FakeClient:
    def __init__(self, payload):
        self._payload = payload
        self.calls = []

    def run_json(self, sys_p, user_p):
        self.calls.append((sys_p, user_p))
        return self._payload


def test_verifier_returns_capped_models_separately_from_rejected():
    """When the verifier accepts more than _DETECTED_MODELS_CAP models, the
    overflow lands in `capped_models` with drop_reason='capped_at_top_5' and
    NEVER in `rejected_models`."""
    n_accepted = _DETECTED_MODELS_CAP + 3
    text = " ".join(f"phrase{i}" for i in range(n_accepted))
    accepted_payload = [
        {
            "model_id": f"model-{i}",
            "presence_mode": "executed",
            "evidence_quote": f"phrase{i}",
            "presence_explanation": "ok",
        }
        for i in range(n_accepted)
    ]
    client = _FakeClient({"accepted": accepted_payload, "rejected": []})
    candidates = [
        {"model_id": f"model-{i}", "model_name": f"Model {i}", "activation_trigger": "x"}
        for i in range(n_accepted)
    ]
    detected, rejected, accepted_before_cap, capped = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(detected) == _DETECTED_MODELS_CAP
    assert len(accepted_before_cap) == n_accepted
    assert len(capped) == 3
    assert all(c["drop_reason"] == "capped_at_top_5" for c in capped)
    # Rejected stays empty: capped is NOT rejected. This is the
    # verification_precision-preservation contract from the design memo.
    assert rejected == []


def test_verifier_no_cap_overflow_returns_empty_capped():
    """When accepted count <= cap, capped is empty and detected ==
    accepted_before_cap by length."""
    accepted_payload = [
        {
            "model_id": "opportunity-cost",
            "presence_mode": "executed",
            "evidence_quote": "weighing the opportunity cost",
            "presence_explanation": "ok",
        }
    ]
    client = _FakeClient({"accepted": accepted_payload, "rejected": []})
    candidates = [
        {"model_id": "opportunity-cost", "model_name": "Opportunity Cost", "activation_trigger": "x"}
    ]
    detected, rejected, accepted_before_cap, capped = run_verification_call_from_packet(
        packet=_packet("weighing the opportunity cost of staying"),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 1
    assert len(accepted_before_cap) == 1
    assert capped == []
    assert rejected == []


# ---------- PipelineConfig.companion_candidate_cap is threaded ----------


def test_pipeline_config_threads_companion_candidate_cap_to_recall():
    """The cap configured in PipelineConfig must reach recall_candidates'
    max_candidates kwarg verbatim — NOT the function default."""
    captured: dict = {}

    def _capture(*, assistant_text, fingerprint_payload, knowledge_graph,
                 reasoning_signals, max_candidates=60, embedding_retriever=None,
                 embedding_api_key=""):  # noqa: ARG001
        captured["max_candidates"] = max_candidates
        return []

    pipeline = SystemBPipeline.__new__(SystemBPipeline)
    pipeline._config = PipelineConfig(
        enable_companion=True,
        enable_embeddings=False,
        companion_candidate_cap=17,  # arbitrary non-default value
    )
    pipeline._boundary = object()
    pipeline._companion_knowledge_graph = {"models": {"x": {}}}
    pipeline._companion_relation_graph = {}
    pipeline._companion_reasoning_signals = {}
    pipeline._embedding_retriever = None
    pipeline._embedding_api_key = ""

    ctx = _ctx("placeholder")
    ir = construct_conversation_ir(ctx)
    with patch(
        "engine.system_b.pipeline.run_fingerprint_call_from_packet",
        return_value=FingerprintPayload(raw=[], validated=[], dropped=[]),
    ), patch(
        "engine.system_b.pipeline.recall_candidates",
        side_effect=_capture,
    ):
        pipeline._run_companion(
            conversation_context=ctx,
            conversation_ir=ir,
            boundary_calls=[],
        )

    assert captured["max_candidates"] == 17
