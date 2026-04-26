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
            "presence_explanation": "ok", "activation_strength": "strong", "why_not_merely_compatible": "answer performs the model's mechanism",
            "activation_strength": "strong",
            "why_not_merely_compatible": "answer performs the model's mechanism",
        }
        for i in range(n_accepted)
    ]
    client = _FakeClient({"accepted": accepted_payload, "rejected": []})
    candidates = [
        {"model_id": f"model-{i}", "model_name": f"Model {i}", "activation_trigger": "x"}
        for i in range(n_accepted)
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, weak_matches, shard_breakdown, traces = run_verification_call_from_packet(
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
            "presence_explanation": "ok", "activation_strength": "strong", "why_not_merely_compatible": "answer performs the model's mechanism",
            "activation_strength": "strong",
            "why_not_merely_compatible": "answer performs the model's mechanism",
        }
    ]
    client = _FakeClient({"accepted": accepted_payload, "rejected": []})
    candidates = [
        {"model_id": "opportunity-cost", "model_name": "Opportunity Cost", "activation_trigger": "x"}
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, weak_matches, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet("weighing the opportunity cost of staying"),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 1
    assert len(accepted_before_cap) == 1
    assert capped == []
    assert rejected == []


# ---------- Verifier dedupe by model_id ----------


def test_verifier_dedupes_duplicate_accepted_model_ids():
    """The verifier sometimes lists the same model_id more than once with
    slightly-different evidence. Dedupe MUST happen before DetectedModel
    construction so downstream CompanionCard.expand_detected_model is not
    called twice for the same source_model_id (which trips the
    'CompanionCard cannot contain more than 3 expansions per detected model'
    invariant). See research/lane2-followup-tracking-2026-04-26.md.

    Pins five guarantees:
    1. Exactly one DetectedModel per unique model_id reaches detected/accepted.
    2. The first valid occurrence's evidence_quote and presence_explanation win.
    3. duplicate_accepts surfaces dropped duplicates with
       drop_reason="duplicate_accept_dedupe".
    4. duplicate_accepts is NOT merged into rejected_models — semantic
       rejection is different and verification_precision telemetry depends
       on rejected meaning rejected.
    5. Subsequent CompanionCard build does not violate the expansion invariant.
    """
    from engine.system_b.companion import build_companion_card
    text = "phrase one and phrase two from the assistant turn"
    accepted_payload = [
        {
            "model_id": "opportunity-cost",
            "presence_mode": "executed",
            "evidence_quote": "phrase one",
            "presence_explanation": "first explanation", "activation_strength": "strong", "why_not_merely_compatible": "answer performs the model's mechanism",
            "activation_strength": "strong",
            "why_not_merely_compatible": "answer performs the model's mechanism",
        },
        {
            "model_id": "opportunity-cost",  # duplicate model_id
            "presence_mode": "executed",
            "evidence_quote": "phrase two",
            "presence_explanation": "second explanation (should be discarded)", "activation_strength": "strong", "why_not_merely_compatible": "answer performs the model's mechanism",
            "activation_strength": "strong",
            "why_not_merely_compatible": "answer performs the model's mechanism",
        },
        {
            "model_id": "opportunity-cost",  # third occurrence — also dropped
            "presence_mode": "violated",
            "evidence_quote": "phrase one and phrase two",
            "presence_explanation": "third explanation (also discarded)", "activation_strength": "strong", "why_not_merely_compatible": "answer performs the model's mechanism",
            "activation_strength": "strong",
            "why_not_merely_compatible": "answer performs the model's mechanism",
        },
    ]
    rejected_payload: list = []
    client = _FakeClient({"accepted": accepted_payload, "rejected": rejected_payload})
    candidates = [
        {"model_id": "opportunity-cost", "model_name": "Opportunity Cost", "activation_trigger": "x"}
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, weak_matches, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    # (1) Exactly one DetectedModel.
    assert len(detected) == 1
    assert len(accepted_before_cap) == 1
    assert detected[0].model_id == "opportunity-cost"
    # (2) First valid occurrence's evidence/explanation wins.
    assert detected[0].evidence_quote == "phrase one"
    assert detected[0].presence_explanation == "first explanation"
    # (3) Duplicates surfaced with the right drop_reason.
    assert len(duplicate_accepts) == 2
    for d in duplicate_accepts:
        assert d["model_id"] == "opportunity-cost"
        assert d["drop_reason"] == "duplicate_accept_dedupe"
    # (4) Not merged into rejected_models.
    assert rejected == []
    assert all(r.get("drop_reason") != "duplicate_accept_dedupe" for r in rejected)
    # (5) CompanionCard build with the deduped detected list does NOT
    #     violate the per-source expansion invariant.
    card = build_companion_card(
        detected_models=detected,
        knowledge_graph={"models": {"opportunity-cost": {"display_name": "Opportunity Cost"}}},
        relation_graph={},
    )
    assert card.detection_model_count == 1


def test_verifier_no_duplicates_yields_empty_duplicate_accepts():
    """Backwards-compat: a payload with no duplicate model_ids produces
    empty duplicate_accepts."""
    text = "weighing the opportunity cost of staying"
    accepted_payload = [
        {
            "model_id": "opportunity-cost",
            "presence_mode": "executed",
            "evidence_quote": "weighing the opportunity cost",
            "presence_explanation": "ok", "activation_strength": "strong", "why_not_merely_compatible": "answer performs the model's mechanism",
            "activation_strength": "strong",
            "why_not_merely_compatible": "answer performs the model's mechanism",
        },
        {
            "model_id": "second-order-thinking",
            "presence_mode": "executed",
            "evidence_quote": "of staying",
            "presence_explanation": "ok", "activation_strength": "strong", "why_not_merely_compatible": "answer performs the model's mechanism",
            "activation_strength": "strong",
            "why_not_merely_compatible": "answer performs the model's mechanism",
        },
    ]
    client = _FakeClient({"accepted": accepted_payload, "rejected": []})
    candidates = [
        {"model_id": "opportunity-cost", "model_name": "Opportunity Cost", "activation_trigger": "x"},
        {"model_id": "second-order-thinking", "model_name": "Second-Order Thinking", "activation_trigger": "x"},
    ]
    detected, rejected, accepted_before_cap, capped, duplicate_accepts, weak_matches, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 2
    assert len(accepted_before_cap) == 2
    assert duplicate_accepts == []
    assert capped == []


# ---------- Partitioned verifier (PR-B) ----------


class _RecordingClient:
    """Sequential boundary client that records each (system_prompt, user_prompt)
    pair plus the payload returned. Used to assert per-bucket call counts and
    that each bucket sees only its own candidates."""

    def __init__(self, payloads_by_bucket_signal: dict[str, dict] | None = None,
                 default_payload: dict | None = None):
        self._payloads = payloads_by_bucket_signal or {}
        self._default = default_payload or {"accepted": [], "rejected": []}
        self.calls: list[tuple[str, str]] = []

    def run_json(self, system_prompt: str, user_prompt: str) -> dict:
        self.calls.append((system_prompt, user_prompt))
        for signal, payload in self._payloads.items():
            if signal in user_prompt:
                return payload
        return self._default


def _candidate(model_id: str, reasoning_type: str, final_rank: int,
               model_name: str | None = None) -> dict:
    return {
        "model_id": model_id,
        "model_name": model_name or model_id.replace("-", " ").title(),
        "activation_trigger": "x",
        "recall_source": "keyword",
        "keyword_rank": final_rank,
        "embedding_rank": None,
        "final_rank": final_rank,
        "reasoning_type": reasoning_type,
    }


def test_verifier_shards_candidates_by_rank_stratification():
    """v3: candidates are sharded by `(final_rank - 1) % 3`. With ranks 1, 2,
    3, 4 → shards 0, 1, 2, 0 → 3 non-empty shards → 3 LLM calls. Stages are
    `companion_verification_shard_<n>`. Each shard prompt contains ONLY its
    own model_ids and shard_breakdown reflects the partition."""
    text = "anchor-A and anchor-B and anchor-C and anchor-D"
    candidates = [
        _candidate("rank-1", "diagnostic",   1),  # shard_0
        _candidate("rank-2", "systems",      2),  # shard_1
        _candidate("rank-3", "probabilistic",3),  # shard_2
        _candidate("rank-4", "metacognitive",4),  # shard_0 (round-robin)
    ]
    client = _RecordingClient(
        payloads_by_bucket_signal={
            # shard_0 contains rank-1 + rank-4. The verifier accepts both.
            "rank-1": {
                "accepted": [
                    {"model_id": "rank-1", "presence_mode": "executed",
                     "evidence_quote": "anchor-A", "presence_explanation": "ok",
                     "activation_strength": "strong", "why_not_merely_compatible": "mechanism"},
                    {"model_id": "rank-4", "presence_mode": "executed",
                     "evidence_quote": "anchor-D", "presence_explanation": "ok",
                     "activation_strength": "strong", "why_not_merely_compatible": "mechanism"},
                ],
                "rejected": [],
            },
            "rank-2": {
                "accepted": [{"model_id": "rank-2", "presence_mode": "executed",
                              "evidence_quote": "anchor-B", "presence_explanation": "ok",
                              "activation_strength": "strong", "why_not_merely_compatible": "mechanism"}],
                "rejected": [],
            },
            "rank-3": {
                "accepted": [{"model_id": "rank-3", "presence_mode": "executed",
                              "evidence_quote": "anchor-C", "presence_explanation": "ok",
                              "activation_strength": "strong", "why_not_merely_compatible": "mechanism"}],
                "rejected": [],
            },
        },
    )
    detected, rejected, accepted_pre, capped, dups, weak, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    # 3 non-empty shards → 3 LLM calls → 3 traces.
    assert len(client.calls) == 3
    assert len(traces) == 3
    stages = sorted(t.stage for t in traces)
    assert stages == ["companion_verification_shard_0", "companion_verification_shard_1", "companion_verification_shard_2"]
    # Each call's user prompt mentions only its shard's model_ids.
    for _, user_prompt in client.calls:
        if "rank-1" in user_prompt:
            # shard_0 also has rank-4 (round-robin); should NOT see rank-2 or rank-3.
            assert "rank-4" in user_prompt
            assert "rank-2" not in user_prompt and "rank-3" not in user_prompt
        elif "rank-2" in user_prompt:
            assert "rank-1" not in user_prompt and "rank-3" not in user_prompt and "rank-4" not in user_prompt
        elif "rank-3" in user_prompt:
            assert "rank-1" not in user_prompt and "rank-2" not in user_prompt and "rank-4" not in user_prompt
    detected_ids = {m.model_id for m in detected}
    assert detected_ids == {"rank-1", "rank-2", "rank-3", "rank-4"}
    # Shard breakdown reflects the round-robin partition.
    assert "shard_0" in shard_breakdown
    assert "shard_1" in shard_breakdown
    assert "shard_2" in shard_breakdown
    assert sorted(shard_breakdown["shard_0"]["accepted"]) == ["rank-1", "rank-4"]
    assert shard_breakdown["shard_1"]["accepted"] == ["rank-2"]
    assert shard_breakdown["shard_2"]["accepted"] == ["rank-3"]
    assert shard_breakdown["shard_0"]["candidate_count"] == 2
    assert shard_breakdown["shard_1"]["candidate_count"] == 1
    assert shard_breakdown["shard_2"]["candidate_count"] == 1


def test_verifier_partition_dedupes_cross_bucket_duplicates():
    """A model_id accepted in two buckets gets deduplicated at fan-in. First
    valid occurrence wins, surplus go to duplicate_accepts (NOT rejected)."""
    text = "phrase-A and phrase-B"
    candidates = [
        _candidate("shared-model", "diagnostic", 1),
        # Duplicate model_id in a different bucket — only happens under
        # list-aware bucketing (deferred). Dedupe must hold either way.
        _candidate("shared-model", "systems", 2),
    ]
    candidates[0]["activation_trigger"] = "anchor:diag"
    candidates[1]["activation_trigger"] = "anchor:sys"
    client = _RecordingClient(
        payloads_by_bucket_signal={
            "anchor:diag": {
                "accepted": [{"model_id": "shared-model", "presence_mode": "executed",
                              "evidence_quote": "phrase-A", "presence_explanation": "diag explanation", "activation_strength": "strong", "why_not_merely_compatible": "answer performs the model's mechanism",}],
                "rejected": [],
            },
            "anchor:sys": {
                "accepted": [{"model_id": "shared-model", "presence_mode": "violated",
                              "evidence_quote": "phrase-B", "presence_explanation": "sys explanation", "activation_strength": "strong", "why_not_merely_compatible": "answer performs the model's mechanism",}],
                "rejected": [],
            },
        },
    )
    detected, rejected, accepted_pre, capped, dups, weak, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 1
    assert detected[0].model_id == "shared-model"
    # First valid occurrence wins (the diagnostic-bucket payload).
    assert detected[0].evidence_quote == "phrase-A"
    assert detected[0].presence_explanation == "diag explanation"
    assert len(dups) == 1
    assert dups[0]["model_id"] == "shared-model"
    assert dups[0]["drop_reason"] == "duplicate_accept_dedupe"
    assert all(r.get("model_id") != "shared-model" for r in rejected)


def test_verifier_partition_sorts_fan_in_by_final_rank_then_model_id():
    """Pre-registered fan-in: (final_rank, model_id). Independent of which
    shard finished first or LLM response order. Protects the top-5 cap from
    parallel-execution non-determinism. Under v3 round-robin sharding,
    candidates with ranks 1..10 land in:
      shard_0: ranks 1, 4, 7, 10
      shard_1: ranks 2, 5, 8
      shard_2: ranks 3, 6, 9
    """
    text = "p1 p2 p3 p4 p5 p6 p7"
    candidates = [
        _candidate("rank-10", "x", 10),  # shard_0
        _candidate("rank-5",  "x", 5),   # shard_1
        _candidate("rank-1",  "x", 1),   # shard_0
        _candidate("rank-2",  "x", 2),   # shard_1
        _candidate("rank-3",  "x", 3),   # shard_2
        _candidate("rank-4",  "x", 4),   # shard_0
    ]
    # Use the LOWEST rank in each shard as the signal — guaranteed unique
    # within shards because the shard partition is rank-based.
    client = _RecordingClient(
        payloads_by_bucket_signal={
            # shard_0 prompt contains rank-1, rank-4, rank-10
            "rank-1": {
                "accepted": [
                    {"model_id": "rank-1", "presence_mode": "executed",
                     "evidence_quote": "p1", "presence_explanation": "ok",
                     "activation_strength": "strong", "why_not_merely_compatible": "mechanism"},
                    {"model_id": "rank-4", "presence_mode": "executed",
                     "evidence_quote": "p4", "presence_explanation": "ok",
                     "activation_strength": "strong", "why_not_merely_compatible": "mechanism"},
                    {"model_id": "rank-10", "presence_mode": "executed",
                     "evidence_quote": "p7", "presence_explanation": "ok",
                     "activation_strength": "strong", "why_not_merely_compatible": "mechanism"},
                ],
                "rejected": [],
            },
            # shard_1 prompt contains rank-2, rank-5
            "rank-2": {
                "accepted": [
                    {"model_id": "rank-2", "presence_mode": "executed",
                     "evidence_quote": "p2", "presence_explanation": "ok",
                     "activation_strength": "strong", "why_not_merely_compatible": "mechanism"},
                    {"model_id": "rank-5", "presence_mode": "executed",
                     "evidence_quote": "p5", "presence_explanation": "ok",
                     "activation_strength": "strong", "why_not_merely_compatible": "mechanism"},
                ],
                "rejected": [],
            },
            # shard_2 prompt contains rank-3
            "rank-3": {
                "accepted": [
                    {"model_id": "rank-3", "presence_mode": "executed",
                     "evidence_quote": "p3", "presence_explanation": "ok",
                     "activation_strength": "strong", "why_not_merely_compatible": "mechanism"},
                ],
                "rejected": [],
            },
        },
    )
    detected, rejected, accepted_pre, capped, dups, weak, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    # Fan-in sort by (final_rank, model_id), independent of shard order.
    assert [m.model_id for m in accepted_pre] == [
        "rank-1", "rank-2", "rank-3", "rank-4", "rank-5", "rank-10",
    ]
    # Top-5 cap applies AFTER the deterministic sort.
    assert [m.model_id for m in detected] == [
        "rank-1", "rank-2", "rank-3", "rank-4", "rank-5",
    ]
    assert len(capped) == 1
    assert capped[0]["model_id"] == "rank-10"


def test_verifier_partition_empty_candidates_short_circuits():
    """No candidates → no LLM calls → empty 6-tuple."""
    client = _RecordingClient()
    detected, rejected, accepted_pre, capped, dups, weak, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet("any text"),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=[],
        client=client,
    )
    assert detected == [] and rejected == [] and accepted_pre == []
    assert capped == [] and dups == [] and traces == []
    assert client.calls == []


def test_verifier_single_shard_runs_one_call():
    """When all candidates' (final_rank - 1) % 3 collapses to the same shard
    (e.g., 1 candidate, or all candidates at ranks {1, 4, 7, ...}), only that
    shard runs. Architecture degenerates cleanly under low-volume cases."""
    text = "phrase-one"
    # All ranks ≡ 0 (mod 3, 0-indexed) → all in shard_0.
    candidates = [
        _candidate("a", "x", 1),  # shard_0
        _candidate("b", "x", 4),  # shard_0
        _candidate("c", "x", 7),  # shard_0
    ]
    client = _RecordingClient(default_payload={
        "accepted": [{"model_id": "a", "presence_mode": "executed",
                      "evidence_quote": "phrase-one", "presence_explanation": "ok", "activation_strength": "strong", "why_not_merely_compatible": "answer performs the model's mechanism",}],
        "rejected": [],
    })
    detected, rejected, accepted_pre, capped, dups, weak, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(client.calls) == 1
    assert len(traces) == 1
    assert traces[0].stage == "companion_verification_shard_0"


# ---------- Strict shared rubric / weak_matches (PR-B v2) ----------


def test_verifier_demotes_accepted_without_activation_strength_to_weak():
    """The shared strict rubric requires `activation_strength="strong"` on
    every accepted item. If the LLM omits it (or sets it to anything other
    than 'strong'), the parser must demote to weak_matches with reason
    'missing_or_non_strong_activation_strength'. Protects against the per-
    bucket verifier becoming under-discriminating after partition removed
    cross-bucket competition."""
    text = "phrase-A and phrase-B"
    accepted_payload = [
        {"model_id": "m-no-strength", "presence_mode": "executed",
         "evidence_quote": "phrase-A", "presence_explanation": "ok",
         "why_not_merely_compatible": "answer performs the mechanism"},
        {"model_id": "m-weak-strength", "presence_mode": "executed",
         "evidence_quote": "phrase-B", "presence_explanation": "ok",
         "activation_strength": "weak",
         "why_not_merely_compatible": "answer performs the mechanism"},
    ]
    candidates = [
        _candidate("m-no-strength",   "diagnostic", 1),
        _candidate("m-weak-strength", "diagnostic", 2),
    ]
    client = _RecordingClient(default_payload={"accepted": accepted_payload, "rejected": []})
    detected, rejected, accepted_pre, capped, dups, weak, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert detected == [] and accepted_pre == []
    weak_by_id = {w["model_id"]: w for w in weak}
    assert "m-no-strength" in weak_by_id
    assert "m-weak-strength" in weak_by_id
    assert weak_by_id["m-no-strength"]["weak_match_reason"] == "missing_or_non_strong_activation_strength"
    assert weak_by_id["m-weak-strength"]["weak_match_reason"] == "missing_or_non_strong_activation_strength"
    rejected_ids = {r.get("model_id") for r in rejected}
    assert "m-no-strength" not in rejected_ids
    assert "m-weak-strength" not in rejected_ids


def test_verifier_demotes_accepted_without_why_not_merely_compatible_to_weak():
    """The shared strict rubric requires `why_not_merely_compatible` on every
    accepted item. Missing or empty → demote to weak_matches. The rubric is
    enforced at the parser, not just the prompt — the LLM cannot bypass it
    by claiming `activation_strength="strong"` while omitting the
    distinction-from-compatibility justification."""
    text = "phrase-A"
    accepted_payload = [
        {"model_id": "m-no-why", "presence_mode": "executed",
         "evidence_quote": "phrase-A", "presence_explanation": "ok",
         "activation_strength": "strong"},
    ]
    candidates = [_candidate("m-no-why", "diagnostic", 1)]
    client = _RecordingClient(default_payload={"accepted": accepted_payload, "rejected": []})
    detected, rejected, accepted_pre, capped, dups, weak, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert detected == [] and accepted_pre == []
    assert len(weak) == 1
    assert weak[0]["model_id"] == "m-no-why"
    assert weak[0]["weak_match_reason"] == "missing_why_not_merely_compatible"


def test_verifier_passes_through_explicit_weak_matches_array():
    """When the LLM puts an item directly in the `weak_matches` array (with
    `weak_match_reason`), it's surfaced as-is. Items not in the candidate
    set are filtered out."""
    text = "phrase-A"
    payload = {
        "accepted": [],
        "rejected": [],
        "weak_matches": [
            {"model_id": "m1", "weak_match_reason": "topic-adjacent"},
            {"model_id": "m2", "weak_match_reason": "compatible_but_not_executed"},
            {"model_id": "m-not-in-candidates", "weak_match_reason": "topic-adjacent"},
        ],
    }
    candidates = [
        _candidate("m1", "diagnostic", 1),
        _candidate("m2", "diagnostic", 2),
    ]
    client = _RecordingClient(default_payload=payload)
    detected, rejected, accepted_pre, capped, dups, weak, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert detected == [] and accepted_pre == [] and rejected == []
    weak_ids = {w["model_id"] for w in weak}
    assert weak_ids == {"m1", "m2"}
    weak_by_id = {w["model_id"]: w for w in weak}
    assert weak_by_id["m1"]["weak_match_reason"] == "topic-adjacent"
    assert weak_by_id["m2"]["weak_match_reason"] == "compatible_but_not_executed"


def test_verifier_strict_rubric_lets_strong_well_specified_items_through():
    """Backwards-compat sanity: when the LLM correctly populates all six
    required fields, the item enters detected — same as before PR-B v2 for
    properly-formatted responses."""
    text = "phrase-A"
    payload = {
        "accepted": [
            {"model_id": "m1", "presence_mode": "executed",
             "evidence_quote": "phrase-A", "presence_explanation": "ok",
             "activation_strength": "strong",
             "why_not_merely_compatible": "the answer performs the mechanism specifically"},
        ],
        "rejected": [],
    }
    candidates = [_candidate("m1", "diagnostic", 1)]
    client = _RecordingClient(default_payload=payload)
    detected, rejected, accepted_pre, capped, dups, weak, shard_breakdown, traces = run_verification_call_from_packet(
        packet=_packet(text),
        fingerprint_payload=FingerprintPayload(raw=[], validated=[], dropped=[]),
        candidates=candidates,
        client=client,
    )
    assert len(detected) == 1
    assert detected[0].model_id == "m1"
    assert weak == []


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
