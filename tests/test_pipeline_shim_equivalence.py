"""Phase 1 shim equivalence: `_context_to_critique` vs legacy `_map_to_critique_request`.

Strategy: compare the CritiqueRequest produced from a ConversationContext
against the dict produced by the legacy mapping function on equivalent
inputs. Bit-identical `query` + `vanilla_answer` is the Phase 1 acceptance
gate; any divergence here is a shim bug.

We also verify `SystemBPipeline.run()` dispatches ConversationContext through
the shim (type-guard check, not a full pipeline execution).
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.conversation_context import (
    ConversationContext,
    DroppedThread,
    ExtractionPayload,
    LiveConstraint,
    Turn,
)
from engine.system_b.pipeline import (
    CritiqueRequest,
    SystemBPipeline,
    _context_to_critique,
)

from scripts.run_extract import (
    _extract_assistant_responses,
    _map_to_critique_request,
)


def _build_equivalent_fixtures(
    *,
    decision_situation: str,
    constraints: list[dict],
    original_framing: str,
    dropped_threads: list[dict],
    synthesized_position: str,
    reasoning_passages: list[str],
    turn_payloads: list[tuple[int, str, str]],  # (turn_index, speaker, text)
) -> tuple[ConversationContext, dict, str, str]:
    """Build matched pair: a ConversationContext and the equivalent inputs
    to `_map_to_critique_request`."""

    context_constraints = tuple(
        LiveConstraint(
            constraint=c["constraint"],
            introduced_turn=c.get("introduced_turn", 1),
            status=c.get("status", "active"),
            weight=c.get("weight", "situational"),
            canonical_key=c.get("canonical_key"),
        )
        for c in constraints
    )
    context_threads = tuple(
        DroppedThread(
            thread=d["thread"],
            raised_by=d.get("raised_by", "user"),
            raised_turn=d.get("raised_turn", 1),
            status=d.get("status", "acknowledged_then_dropped"),
            superseded_by=d.get("superseded_by"),
        )
        for d in dropped_threads
    )
    turns = tuple(
        Turn(turn_index=i, speaker=s, text=t) for (i, s, t) in turn_payloads
    )
    context = ConversationContext(
        turns=turns,
        extraction=ExtractionPayload(
            decision_situation=decision_situation,
            live_constraints=context_constraints,
            synthesized_position=synthesized_position,
            reasoning_passages=tuple(reasoning_passages),
            original_framing=original_framing,
            dropped_threads=context_threads,
        ),
    )

    extraction_dict = {
        "decision_situation": decision_situation,
        "live_constraints": constraints,
        "synthesized_position": synthesized_position,
        "reasoning_passages": reasoning_passages,
        "original_framing": original_framing,
        "dropped_threads": dropped_threads,
    }

    # Rebuild the conversation text in the same shape run_extract.py parses
    # so _extract_assistant_responses sees identical input to what the
    # loader saw. Header is purely cosmetic here — the function keys on the
    # [Turn N] markers.
    conversation_lines = ["CONVERSATION: synthetic"]
    conversation_lines.append("")
    for (turn_index, speaker, text) in turn_payloads:
        conversation_lines.append(f"[Turn {turn_index}] {speaker.upper()}:")
        conversation_lines.append(text)
        conversation_lines.append("")
    conversation_text = "\n".join(conversation_lines)
    assistant_text = _extract_assistant_responses(conversation_text)

    return context, extraction_dict, assistant_text, conversation_text


def _assert_bit_identical(context: ConversationContext, extraction_dict: dict, assistant_text: str) -> None:
    shim_result = _context_to_critique(context)
    legacy_result = _map_to_critique_request(extraction_dict, assistant_text=assistant_text)

    assert shim_result.query == legacy_result["query"], (
        f"query diverged:\nshim:  {shim_result.query!r}\n"
        f"legacy: {legacy_result['query']!r}"
    )
    assert shim_result.vanilla_answer == legacy_result["vanilla_answer"], (
        f"vanilla_answer diverged:\n"
        f"shim:   {shim_result.vanilla_answer!r}\n"
        f"legacy: {legacy_result['vanilla_answer']!r}"
    )


# ---------- Equivalence cases ----------


def test_simple_case_no_constraints_short_assistant_text() -> None:
    context, extraction_dict, assistant_text, _ = _build_equivalent_fixtures(
        decision_situation="Should I take the offer?",
        constraints=[],
        original_framing="",
        dropped_threads=[],
        synthesized_position="Take it with conditions.",
        reasoning_passages=["quote a", "quote b"],
        turn_payloads=[
            (1, "user", "Should I take it?"),
            (1, "assistant", "short reply"),
        ],
    )
    _assert_bit_identical(context, extraction_dict, assistant_text)


def test_full_case_constraints_framing_threads_long_assistant_text() -> None:
    long_assistant = (
        "This is a long assistant reply that is clearly over 200 characters. "
        * 10
    )
    context, extraction_dict, assistant_text, _ = _build_equivalent_fixtures(
        decision_situation="Accept the new role or stay?",
        constraints=[
            {
                "constraint": "salary 3x current",
                "introduced_turn": 1,
                "status": "active",
                "weight": "structural",
                "canonical_key": "salary-3x",
            },
            {
                "constraint": "commute 3 days/week",
                "introduced_turn": 1,
                "status": "active",
                "weight": "situational",
            },
        ],
        original_framing="Is this obvious or crazy?",
        dropped_threads=[
            {
                "thread": "husband career impact",
                "raised_by": "user",
                "raised_turn": 2,
                "status": "acknowledged_then_dropped",
                "superseded_by": "financial framing took over",
            },
            {
                "thread": "fellowship mentorship continuity",
                "raised_by": "user",
                "raised_turn": 2,
                "status": "acknowledged_then_dropped",
                "superseded_by": None,
            },
        ],
        synthesized_position="Accept with explicit conditions on commute cadence.",
        reasoning_passages=["passage 1", "passage 2"],
        turn_payloads=[
            (1, "user", "Offer context..."),
            (1, "assistant", long_assistant),
            (2, "user", "Follow-up"),
            (2, "assistant", long_assistant),
        ],
    )
    _assert_bit_identical(context, extraction_dict, assistant_text)


def test_constraint_status_active_tag_omits_weight() -> None:
    context, extraction_dict, assistant_text, _ = _build_equivalent_fixtures(
        decision_situation="X",
        constraints=[
            {
                "constraint": "C",
                "introduced_turn": 1,
                "status": "active",
                "weight": "structural",
            }
        ],
        original_framing="",
        dropped_threads=[],
        synthesized_position="",
        reasoning_passages=[],
        turn_payloads=[(1, "user", "q"), (1, "assistant", "a")],
    )
    _assert_bit_identical(context, extraction_dict, assistant_text)
    # Sanity: the "active" status should NOT put weight in the tag
    assert "[ACTIVE]" in _context_to_critique(context).query
    assert "STRUCTURAL" not in _context_to_critique(context).query.split("\n", 1)[1].split("Original", 1)[0]


def test_constraint_status_dropped_tag_includes_weight() -> None:
    context, extraction_dict, assistant_text, _ = _build_equivalent_fixtures(
        decision_situation="X",
        constraints=[
            {
                "constraint": "C",
                "introduced_turn": 1,
                "status": "dropped",
                "weight": "structural",
            }
        ],
        original_framing="",
        dropped_threads=[],
        synthesized_position="",
        reasoning_passages=[],
        turn_payloads=[(1, "user", "q"), (1, "assistant", "a")],
    )
    _assert_bit_identical(context, extraction_dict, assistant_text)
    assert "[DROPPED/STRUCTURAL]" in _context_to_critique(context).query


def test_vanilla_answer_fallback_mode_when_no_assistant_text() -> None:
    """No assistant turns → fallback (synthesized_position + reasoning_passages)."""
    context, extraction_dict, assistant_text, _ = _build_equivalent_fixtures(
        decision_situation="X",
        constraints=[],
        original_framing="",
        dropped_threads=[],
        synthesized_position="Position summary.",
        reasoning_passages=["p1", "p2", "p3"],
        turn_payloads=[(1, "user", "q")],  # user-only
    )
    _assert_bit_identical(context, extraction_dict, assistant_text)
    shim_out = _context_to_critique(context)
    assert 'Key reasoning passages from the conversation' in shim_out.vanilla_answer


def test_vanilla_answer_full_mode_when_long_assistant_text() -> None:
    long_ = "x" * 500
    context, extraction_dict, assistant_text, _ = _build_equivalent_fixtures(
        decision_situation="X",
        constraints=[],
        original_framing="",
        dropped_threads=[],
        synthesized_position="syn",
        reasoning_passages=["p"],
        turn_payloads=[(1, "user", "q"), (1, "assistant", long_)],
    )
    _assert_bit_identical(context, extraction_dict, assistant_text)
    shim_out = _context_to_critique(context)
    assert shim_out.vanilla_answer.startswith("SYNTHESIZED POSITION:")
    assert "FULL ASSISTANT REASONING:" in shim_out.vanilla_answer


def test_multi_turn_assistant_joined_with_separator() -> None:
    long_a = "A" * 150
    long_b = "B" * 150
    context, extraction_dict, assistant_text, _ = _build_equivalent_fixtures(
        decision_situation="X",
        constraints=[],
        original_framing="",
        dropped_threads=[],
        synthesized_position="syn",
        reasoning_passages=[],
        turn_payloads=[
            (1, "user", "q1"),
            (1, "assistant", long_a),
            (2, "user", "q2"),
            (2, "assistant", long_b),
        ],
    )
    _assert_bit_identical(context, extraction_dict, assistant_text)
    # Shim must use the same "\n\n---\n\n" separator as the legacy regex join
    shim_out = _context_to_critique(context)
    assert "\n\n---\n\n" in shim_out.vanilla_answer


def test_dropped_thread_without_superseded_by_omits_arrow() -> None:
    context, extraction_dict, assistant_text, _ = _build_equivalent_fixtures(
        decision_situation="X",
        constraints=[],
        original_framing="",
        dropped_threads=[
            {
                "thread": "T",
                "raised_by": "user",
                "raised_turn": 1,
                "status": "acknowledged_then_dropped",
                "superseded_by": None,
            }
        ],
        synthesized_position="",
        reasoning_passages=[],
        turn_payloads=[(1, "user", "q"), (1, "assistant", "a")],
    )
    _assert_bit_identical(context, extraction_dict, assistant_text)
    assert "→" not in _context_to_critique(context).query


# ---------- Dispatch ----------


def test_run_dispatches_conversation_context_through_shim() -> None:
    """SystemBPipeline.run() must route ConversationContext through _context_to_critique."""
    ctx = ConversationContext(
        turns=(Turn(turn_index=1, speaker="user", text="q"),),
        extraction=ExtractionPayload(
            decision_situation="D",
            live_constraints=(),
            synthesized_position="S",
            reasoning_passages=(),
            original_framing="",
            dropped_threads=(),
        ),
    )

    captured: list = []

    def _spy_converter(context: ConversationContext) -> CritiqueRequest:
        captured.append(context)
        raise _ShimDispatchedException()

    with patch(
        "engine.system_b.pipeline._context_to_critique",
        side_effect=_spy_converter,
    ):
        pipeline = SystemBPipeline.__new__(SystemBPipeline)  # skip __init__ setup
        try:
            pipeline.run(ctx)
        except _ShimDispatchedException:
            pass

    assert len(captured) == 1
    assert captured[0] is ctx


def test_run_passes_critique_request_through_without_shim() -> None:
    """A CritiqueRequest must NOT trigger the shim conversion."""
    critique = CritiqueRequest(query="q", vanilla_answer="a")

    def _fail_if_called(context: ConversationContext) -> CritiqueRequest:
        raise AssertionError("shim should not run for CritiqueRequest input")

    with patch(
        "engine.system_b.pipeline._context_to_critique",
        side_effect=_fail_if_called,
    ):
        pipeline = SystemBPipeline.__new__(SystemBPipeline)
        # The pipeline will crash downstream because we haven't set up state,
        # but it must get past the dispatch without calling the shim.
        try:
            pipeline.run(critique)
        except AttributeError:
            # downstream access to self._boundary etc. — expected without __init__
            pass


class _ShimDispatchedException(Exception):
    pass


# ---------- Phase 2a: Lane 3 dispatch ----------


def _minimal_context() -> ConversationContext:
    return ConversationContext(
        turns=(Turn(turn_index=1, speaker="user", text="question text"),),
        extraction=ExtractionPayload(
            decision_situation="D",
            live_constraints=(),
            synthesized_position="S",
            reasoning_passages=(),
            original_framing="",
            dropped_threads=(),
        ),
    )


def test_run_frame_pressure_uses_context_path_when_context_present() -> None:
    """When _run_frame_pressure is given a ConversationContext, Lane 3 must
    call run_frame_extraction_from_context (not the legacy query-based one)."""
    from engine.system_b.pipeline import PipelineConfig
    ctx = _minimal_context()
    captured_from_context: list = []
    captured_legacy: list = []

    def _spy_from_context(*, boundary, context):  # noqa: ARG001
        captured_from_context.append(context)
        raise _ShimDispatchedException()

    def _spy_legacy(*, boundary, query, vanilla_answer):  # noqa: ARG001
        captured_legacy.append((query, vanilla_answer))
        raise _ShimDispatchedException()

    with patch(
        "engine.system_b.pipeline.run_frame_extraction_from_context",
        side_effect=_spy_from_context,
    ), patch(
        "engine.system_b.pipeline.run_frame_extraction",
        side_effect=_spy_legacy,
    ):
        pipeline = SystemBPipeline.__new__(SystemBPipeline)
        pipeline._config = PipelineConfig(enable_frame_pressure=True)
        pipeline._boundary = object()
        try:
            pipeline._run_frame_pressure(
                CritiqueRequest(query="legacy_q", vanilla_answer="legacy_va"),
                boundary_calls=[],
                conversation_context=ctx,
            )
        except _ShimDispatchedException:
            pass

    assert len(captured_from_context) == 1
    assert captured_from_context[0] is ctx
    assert captured_legacy == [], "legacy run_frame_extraction should NOT have been called"


def test_run_frame_pressure_uses_legacy_path_when_no_context() -> None:
    """Without a ConversationContext, _run_frame_pressure must keep calling the
    legacy run_frame_extraction path — protects the existing shim behavior."""
    from engine.system_b.pipeline import PipelineConfig
    critique = CritiqueRequest(query="qtext", vanilla_answer="vatext")
    captured_from_context: list = []
    captured_legacy: list = []

    def _spy_from_context(*, boundary, context):  # noqa: ARG001
        captured_from_context.append(context)
        raise _ShimDispatchedException()

    def _spy_legacy(*, boundary, query, vanilla_answer):  # noqa: ARG001
        captured_legacy.append((query, vanilla_answer))
        raise _ShimDispatchedException()

    with patch(
        "engine.system_b.pipeline.run_frame_extraction_from_context",
        side_effect=_spy_from_context,
    ), patch(
        "engine.system_b.pipeline.run_frame_extraction",
        side_effect=_spy_legacy,
    ):
        pipeline = SystemBPipeline.__new__(SystemBPipeline)
        pipeline._config = PipelineConfig(enable_frame_pressure=True)
        pipeline._boundary = object()
        try:
            pipeline._run_frame_pressure(
                critique,
                boundary_calls=[],
                conversation_context=None,
            )
        except _ShimDispatchedException:
            pass

    assert len(captured_legacy) == 1
    assert captured_legacy[0] == ("qtext", "vatext")
    assert captured_from_context == [], "new from_context path should NOT have been called"


def test_run_frame_pressure_skips_both_paths_when_feature_disabled() -> None:
    """PipelineConfig.enable_frame_pressure=False short-circuits Lane 3 entirely."""
    from engine.system_b.pipeline import PipelineConfig
    pipeline = SystemBPipeline.__new__(SystemBPipeline)
    pipeline._config = PipelineConfig(enable_frame_pressure=False)
    pipeline._boundary = object()
    result = pipeline._run_frame_pressure(
        CritiqueRequest(query="q", vanilla_answer="a"),
        boundary_calls=[],
        conversation_context=_minimal_context(),
    )
    assert result is None


# ---------- Phase 2b: Lane 4 dispatch ----------


def test_run_structural_coverage_uses_context_path_when_context_present() -> None:
    """Given a ConversationContext, Lane 4 must call
    run_structural_coverage_from_context (not the legacy orchestrator)."""
    from engine.system_b.pipeline import PipelineConfig
    ctx = _minimal_context()
    captured_from_context: list = []
    captured_legacy: list = []

    def _spy_from_context(*, boundary, context, structural_coverage_routing, anti_echo_model_ids):  # noqa: ARG001
        captured_from_context.append(context)
        raise _ShimDispatchedException()

    def _spy_legacy(*, boundary, query, vanilla_answer, structural_coverage_routing, anti_echo_model_ids):  # noqa: ARG001
        captured_legacy.append((query, vanilla_answer))
        raise _ShimDispatchedException()

    with patch(
        "engine.system_b.pipeline.run_structural_coverage_from_context",
        side_effect=_spy_from_context,
    ), patch(
        "engine.system_b.pipeline.run_structural_coverage",
        side_effect=_spy_legacy,
    ):
        pipeline = SystemBPipeline.__new__(SystemBPipeline)
        pipeline._config = PipelineConfig(enable_structural_coverage=True)
        pipeline._boundary = object()
        pipeline._companion_knowledge_graph = {"structural_coverage_routing": {"dimensions": {}}}
        try:
            pipeline._run_structural_coverage(
                CritiqueRequest(query="legacy_q", vanilla_answer="legacy_va"),
                boundary_calls=[],
                lane1_model_ids=set(),
                lane2_model_ids=set(),
                lane3_model_ids=set(),
                conversation_context=ctx,
            )
        except _ShimDispatchedException:
            pass

    assert len(captured_from_context) == 1
    assert captured_from_context[0] is ctx
    assert captured_legacy == [], "legacy run_structural_coverage should NOT have been called"


def test_run_structural_coverage_uses_legacy_path_when_no_context() -> None:
    """Without a ConversationContext, Lane 4 must keep calling the legacy path."""
    from engine.system_b.pipeline import PipelineConfig
    critique = CritiqueRequest(query="qtext", vanilla_answer="vatext")
    captured_from_context: list = []
    captured_legacy: list = []

    def _spy_from_context(*, boundary, context, structural_coverage_routing, anti_echo_model_ids):  # noqa: ARG001
        captured_from_context.append(context)
        raise _ShimDispatchedException()

    def _spy_legacy(*, boundary, query, vanilla_answer, structural_coverage_routing, anti_echo_model_ids):  # noqa: ARG001
        captured_legacy.append((query, vanilla_answer))
        raise _ShimDispatchedException()

    with patch(
        "engine.system_b.pipeline.run_structural_coverage_from_context",
        side_effect=_spy_from_context,
    ), patch(
        "engine.system_b.pipeline.run_structural_coverage",
        side_effect=_spy_legacy,
    ):
        pipeline = SystemBPipeline.__new__(SystemBPipeline)
        pipeline._config = PipelineConfig(enable_structural_coverage=True)
        pipeline._boundary = object()
        pipeline._companion_knowledge_graph = {"structural_coverage_routing": {"dimensions": {}}}
        try:
            pipeline._run_structural_coverage(
                critique,
                boundary_calls=[],
                lane1_model_ids=set(),
                lane2_model_ids=set(),
                lane3_model_ids=set(),
                conversation_context=None,
            )
        except _ShimDispatchedException:
            pass

    assert len(captured_legacy) == 1
    assert captured_legacy[0] == ("qtext", "vatext")
    assert captured_from_context == [], "new from_context path should NOT have been called"


def test_run_structural_coverage_skips_both_paths_when_feature_disabled() -> None:
    """enable_structural_coverage=False short-circuits Lane 4 entirely."""
    from engine.system_b.pipeline import PipelineConfig
    pipeline = SystemBPipeline.__new__(SystemBPipeline)
    pipeline._config = PipelineConfig(enable_structural_coverage=False)
    pipeline._boundary = object()
    result = pipeline._run_structural_coverage(
        CritiqueRequest(query="q", vanilla_answer="a"),
        boundary_calls=[],
        lane1_model_ids=set(),
        lane2_model_ids=set(),
        lane3_model_ids=set(),
        conversation_context=_minimal_context(),
    )
    assert result is None
