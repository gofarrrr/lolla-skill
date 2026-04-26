"""ConversationContext-only runtime tests for the Phase 6 contract.

These tests replace the old shim-equivalence suite after the pipeline stops
accepting legacy flat-request runtime inputs.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.companion import FingerprintPayload
from engine.system_b.conversation_context import (
    ConversationContext,
    ExtractionPayload,
    Turn,
)
from engine.system_b.frame_pressure import (
    ExtractedFrameElement,
    FramePressureCard,
)
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.pipeline import (
    CompanionRunResult,
    PipelineConfig,
    SystemBPipeline,
    _run_pass1_clusters_parallel,
)


def _ctx(
    *,
    user_text: str = "Should I take the offer?",
    assistant_text: str = "Take it with safeguards.",
    synthesized_position: str = "SYNTH SHOULD NOT DRIVE RUNTIME READERS",
) -> ConversationContext:
    return ConversationContext(
        turns=(
            Turn(turn_index=1, speaker="user", text=user_text),
            Turn(turn_index=2, speaker="assistant", text=assistant_text),
        ),
        extraction=ExtractionPayload(
            decision_situation="Whether to take the offer",
            live_constraints=(),
            synthesized_position=synthesized_position,
            reasoning_passages=(),
            original_framing="Is this worth it?",
            dropped_threads=(),
        ),
    )


class _RecordingBoundary:
    supports_parallel_calls = False

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def run_json(self, system_prompt: str, user_prompt: str) -> dict:
        self.calls.append((system_prompt, user_prompt))
        return {"scores": [], "detected": False, "reason": "stub"}


def _lane1_minimal_catalog():
    from engine.system_b.tendency_catalog import ModelBinding, TendencyCatalog, TendencyRef

    tendency = TendencyRef(
        tendency_id="authority-misinfluence-tendency",
        display_name="Authority Misinfluence Tendency",
        routing_key="authority_misinfluence",
        antidote_model_ids=("first-principles-thinking",),
        antidote_bindings=(ModelBinding(model_id="first-principles-thinking"),),
        description="Prestige substitutes for evidence.",
        tendency_number=7,
    )
    return TendencyCatalog(
        tendencies={"authority-misinfluence-tendency": tendency},
        alias_index={
            "authority-misinfluence": "authority-misinfluence-tendency",
            "authority-misinfluence-tendency": "authority-misinfluence-tendency",
        },
    )


def test_pipeline_run_requires_conversation_context() -> None:
    pipeline = SystemBPipeline.__new__(SystemBPipeline)

    with pytest.raises(TypeError, match="ConversationContext"):
        pipeline.run(object())


def test_run_pass1_clusters_parallel_uses_context_prompt_shape() -> None:
    boundary = _RecordingBoundary()
    catalog = _lane1_minimal_catalog()
    context = _ctx()

    _run_pass1_clusters_parallel(
        conversation_context=context,
        boundary=boundary,
        catalog=catalog,
    )

    assert len(boundary.calls) == 6
    for _, user_prompt in boundary.calls:
        assert "CONTEXT" in user_prompt
        assert "SOURCE" in user_prompt
        assert "Take it with safeguards." in user_prompt


def test_pipeline_run_uses_joined_assistant_turns_for_embedding_signal() -> None:
    context = _ctx(
        assistant_text="Use the assistant turns, not synthesized_position.",
        synthesized_position="SHOULD NOT BE USED HERE",
    )
    captured: dict[str, str] = {}

    def _capture_embedding_input(*, assistant_text, retriever, api_key):  # noqa: ARG001
        captured["assistant_text"] = assistant_text
        return {}

    pipeline = SystemBPipeline.__new__(SystemBPipeline)
    pipeline._config = PipelineConfig(
        enable_companion=False,
        enable_frame_pressure=False,
        enable_structural_coverage=False,
        enable_embeddings=True,
    )
    pipeline._boundary = object()
    pipeline._catalog = SimpleNamespace(warnings=())
    pipeline._embedding_retriever = object()
    pipeline._embedding_api_key = "test-key"
    pipeline._prompt_versions = ()
    pipeline._telemetry_store = None
    pipeline._companion_knowledge_graph = {}
    pipeline._bundle_selector = None

    with patch("engine.system_b.pipeline._run_pass1_clusters_parallel", return_value=([], [])), \
         patch("engine.system_b.pipeline._embedding_tendency_signal", side_effect=_capture_embedding_input):
        pipeline._build_lane1_relevance_scores = lambda query_text: None  # type: ignore[method-assign]
        pipeline.run(context)

    assert captured["assistant_text"] == "Use the assistant turns, not synthesized_position."


def test_run_companion_recall_uses_joined_assistant_turns() -> None:
    context = _ctx(
        assistant_text="Assistant reasoning should feed recall.",
        synthesized_position="SYNTH SHOULD NOT DRIVE RECALL",
    )
    conversation_ir = construct_conversation_ir(context)
    captured: dict[str, str] = {}

    pipeline = SystemBPipeline.__new__(SystemBPipeline)
    pipeline._config = PipelineConfig(enable_companion=True, enable_embeddings=False)
    pipeline._boundary = object()
    pipeline._companion_knowledge_graph = {"models": {"first-principles-thinking": {}}}
    pipeline._companion_relation_graph = {}
    pipeline._companion_reasoning_signals = {}
    pipeline._embedding_retriever = None
    pipeline._embedding_api_key = ""

    def _capture_recall(*, assistant_text, fingerprint_payload, knowledge_graph, reasoning_signals, max_candidates=60, embedding_retriever=None, embedding_api_key=""):  # noqa: ARG001
        captured["assistant_text"] = assistant_text
        captured["max_candidates"] = max_candidates
        return []

    with patch(
        "engine.system_b.pipeline.run_fingerprint_call_from_packet",
        return_value=FingerprintPayload(raw=[], validated=[], dropped=[]),
    ), patch(
        "engine.system_b.pipeline.recall_candidates",
        side_effect=_capture_recall,
    ):
        result = pipeline._run_companion(
            conversation_context=context,
            conversation_ir=conversation_ir,
            boundary_calls=[],
        )

    assert isinstance(result, CompanionRunResult)
    assert captured["assistant_text"] == "Assistant reasoning should feed recall."


def test_run_frame_pressure_uses_packet_extraction_and_context_reframing() -> None:
    context = _ctx()
    conversation_ir = construct_conversation_ir(context)
    packet_calls: list[object] = []
    reframing_calls: list[ConversationContext] = []

    pipeline = SystemBPipeline.__new__(SystemBPipeline)
    pipeline._config = PipelineConfig(enable_frame_pressure=True)
    pipeline._boundary = object()
    pipeline._companion_knowledge_graph = {
        "reframing_routing": {
            "binary_collapse": ["first-principles-thinking"],
        }
    }

    extraction_result = FramePressureCard(
        frame_elements=(
            ExtractedFrameElement(
                element_text="binary framing",
                element_type="assumption",
                evidence_quote="Should I take the offer?",
                frame_pattern="binary_collapse",
                fragility_signal="other options exist",
                inquiry_stage="why",
                likely_default="none",
            ),
        ),
    )

    def _capture_packet(*, boundary, packet):  # noqa: ARG001
        packet_calls.append(packet)
        return extraction_result

    def _capture_reframings(*, boundary, context, elements, routes):  # noqa: ARG001
        reframing_calls.append(context)
        return ()

    with patch(
        "engine.system_b.pipeline.run_frame_extraction_from_packet",
        side_effect=_capture_packet,
    ), patch(
        "engine.system_b.pipeline.generate_reframings_from_context",
        side_effect=_capture_reframings,
    ):
        card = pipeline._run_frame_pressure(
            conversation_context=context,
            conversation_ir=conversation_ir,
            boundary_calls=[],
            lane1_tendency_ids=set(),
            lane1_model_ids=set(),
        )

    assert card is not None
    assert len(packet_calls) == 1
    assert reframing_calls == [context]


def test_run_lane4_structural_coverage_uses_ir_path() -> None:
    context = _ctx()
    conversation_ir = construct_conversation_ir(context)
    captured_irs: list[object] = []

    pipeline = SystemBPipeline.__new__(SystemBPipeline)
    pipeline._config = PipelineConfig(enable_structural_coverage=True)
    pipeline._boundary = object()
    pipeline._companion_knowledge_graph = {"structural_coverage_routing": {"dimensions": {}}}

    def _capture_ir(*, boundary, ir, structural_coverage_routing, anti_echo_model_ids):  # noqa: ARG001
        captured_irs.append(ir)
        return None

    with patch(
        "engine.system_b.pipeline.run_structural_coverage_from_ir",
        side_effect=_capture_ir,
    ):
        pipeline._run_lane4_structural_coverage(
            conversation_ir=conversation_ir,
            boundary_calls=[],
            lane1_model_ids=set(),
            lane2_model_ids=set(),
            lane3_model_ids=set(),
        )

    assert captured_irs == [conversation_ir]
