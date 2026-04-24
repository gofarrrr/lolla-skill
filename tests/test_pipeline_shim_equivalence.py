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


# ---------- Phase 2c: Lane 1 dispatch ----------
#
# Unlike Lane 3/4 (single orchestrator function), Lane 1 has two call sites
# — _run_pass1_clusters_parallel + _run_pass2_parallel — and both must
# dispatch on the presence of conversation_context. We test the dispatch by
# giving each call a stub BoundaryClient that records the (system, user)
# prompts received and asserting on the shape of the user prompts (CONTEXT
# vs QUERY markers).

class _RecordingBoundary:
    """Minimal BoundaryClient-shaped stub. Records prompts passed in and
    returns canned JSON so Pass 1 / Pass 2 parsers don't error out."""

    supports_parallel_calls = False  # force sequential fallback (simpler)

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def run_json(self, system_prompt: str, user_prompt: str) -> dict:
        self.calls.append((system_prompt, user_prompt))
        return {"scores": [], "detected": False, "reason": "stub"}

    def last_call_trace(self) -> dict:
        return {"stage": "stub", "status": "ok", "latency_ms": 0}


def _lane1_context_with_assistant() -> ConversationContext:
    """Context with both user and assistant turns so Pass 1 SOURCE has material."""
    return ConversationContext(
        turns=(
            Turn(turn_index=1, speaker="user", text="Should I take the Series B offer at 15%?"),
            Turn(turn_index=2, speaker="assistant", text="You should take it — 15% is typical."),
        ),
        extraction=ExtractionPayload(
            decision_situation="Founder considers Series B offer",
            live_constraints=(),
            synthesized_position="take the offer",
            reasoning_passages=(),
            original_framing="Is 15% too low?",
            dropped_threads=(),
        ),
    )


def _lane1_minimal_catalog():
    """Minimal catalog with one tendency for Pass 2 dispatch tests."""
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


def test_run_pass1_clusters_parallel_uses_context_path_when_context_present() -> None:
    """When conversation_context is provided, Pass 1 cluster prompts must
    use the CONTEXT/SOURCE shape (not legacy query+vanilla_answer)."""
    from engine.system_b.pipeline import _run_pass1_clusters_parallel
    catalog = _lane1_minimal_catalog()
    boundary = _RecordingBoundary()
    ctx = _lane1_context_with_assistant()

    _run_pass1_clusters_parallel(
        request=CritiqueRequest(query="LEGACY_QUERY_SHOULD_NOT_APPEAR", vanilla_answer="LEGACY_VA_SHOULD_NOT_APPEAR"),
        boundary=boundary,
        catalog=catalog,
        conversation_context=ctx,
    )

    # Expect 6 cluster calls; every user prompt must carry CONTEXT/SOURCE markers
    # and must NOT use legacy-only markers.
    assert len(boundary.calls) == 6
    for _, user in boundary.calls:
        assert "CONTEXT" in user
        assert "SOURCE" in user
        # The assistant turn should be quoted verbatim in SOURCE
        assert "You should take it" in user
        # Legacy markers must not appear
        assert "LEGACY_QUERY_SHOULD_NOT_APPEAR" not in user
        assert "LEGACY_VA_SHOULD_NOT_APPEAR" not in user


def test_run_pass1_clusters_parallel_uses_legacy_path_when_no_context() -> None:
    """Without a conversation_context, Pass 1 must keep using the legacy
    query+vanilla_answer template."""
    from engine.system_b.pipeline import _run_pass1_clusters_parallel
    catalog = _lane1_minimal_catalog()
    boundary = _RecordingBoundary()

    _run_pass1_clusters_parallel(
        request=CritiqueRequest(query="LEGACY_Q_VERBATIM", vanilla_answer="LEGACY_VA_VERBATIM"),
        boundary=boundary,
        catalog=catalog,
        conversation_context=None,
    )

    assert len(boundary.calls) == 6
    for _, user in boundary.calls:
        assert "LEGACY_Q_VERBATIM" in user
        assert "LEGACY_VA_VERBATIM" in user
        # New-path markers must not appear
        assert "CONTEXT" not in user or "VANILLA ANSWER" in user  # legacy template has "ANSWER", not "CONTEXT"
        # Stricter: must not have the SOURCE section header
        assert "SOURCE (PRIMARY AUDIT TARGET" not in user


def test_run_pass2_parallel_uses_context_path_when_context_present() -> None:
    """When conversation_context is provided, Pass 2 must use
    format_pass2_prompt_from_context (CONTEXT/SOURCE shape + enum-checklist)."""
    from engine.system_b.pipeline import TriggeredTendency, _run_pass2_parallel
    catalog = _lane1_minimal_catalog()
    boundary = _RecordingBoundary()
    ctx = _lane1_context_with_assistant()
    triggered = (TriggeredTendency(tendency_id="authority-misinfluence-tendency", source="triage", score=6),)

    _run_pass2_parallel(
        triggered_tendencies=triggered,
        request=CritiqueRequest(query="LEGACY_Q_NO", vanilla_answer="LEGACY_VA_NO"),
        boundary=boundary,
        catalog=catalog,
        conversation_context=ctx,
    )

    assert len(boundary.calls) == 1
    system, user = boundary.calls[0]
    assert "CONTEXT" in user
    assert "SOURCE" in user
    assert "You should take it" in user
    # Legacy markers must not appear
    assert "LEGACY_Q_NO" not in user
    assert "LEGACY_VA_NO" not in user
    # Enum-checklist reminder must be present in system prompt (2b durable lesson)
    assert "ENUM CHECKLIST REMINDER" in system or "consider each" in system.lower()


def test_run_pass2_parallel_uses_legacy_path_when_no_context() -> None:
    """Without conversation_context, Pass 2 must keep using the legacy prompt."""
    from engine.system_b.pipeline import TriggeredTendency, _run_pass2_parallel
    catalog = _lane1_minimal_catalog()
    boundary = _RecordingBoundary()
    triggered = (TriggeredTendency(tendency_id="authority-misinfluence-tendency", source="triage", score=6),)

    _run_pass2_parallel(
        triggered_tendencies=triggered,
        request=CritiqueRequest(query="LEGACY_Q_YES", vanilla_answer="LEGACY_VA_YES"),
        boundary=boundary,
        catalog=catalog,
        conversation_context=None,
    )

    assert len(boundary.calls) == 1
    _, user = boundary.calls[0]
    assert "LEGACY_Q_YES" in user
    assert "LEGACY_VA_YES" in user
    # New-path SOURCE section header must not appear
    assert "SOURCE (PRIMARY AUDIT TARGET" not in user


# ---------- Phase 2d: Lane 2 (Companion) dispatch ----------


def test_run_companion_uses_context_path_when_context_present() -> None:
    """With a ConversationContext, Lane 2 must call the `_from_context`
    fingerprint + verification helpers, not the legacy `vanilla_answer` ones."""
    from engine.system_b.pipeline import PipelineConfig
    ctx = _minimal_context()
    captured_ctx_fp: list = []
    captured_ctx_ver: list = []
    captured_legacy_fp: list = []
    captured_legacy_ver: list = []

    def _fp_ctx(*, context, client):  # noqa: ARG001
        captured_ctx_fp.append(context)
        raise _ShimDispatchedException()

    def _ver_ctx(*, context, fingerprint_payload, candidates, client):  # noqa: ARG001
        captured_ctx_ver.append(context)
        raise _ShimDispatchedException()

    def _fp_legacy(*, query, vanilla_answer, client):  # noqa: ARG001
        captured_legacy_fp.append((query, vanilla_answer))
        raise _ShimDispatchedException()

    def _ver_legacy(*, vanilla_answer, fingerprint_payload, candidates, client):  # noqa: ARG001
        captured_legacy_ver.append(vanilla_answer)
        raise _ShimDispatchedException()

    with patch("engine.system_b.pipeline.run_fingerprint_call_from_context", side_effect=_fp_ctx), \
         patch("engine.system_b.pipeline.run_verification_call_from_context", side_effect=_ver_ctx), \
         patch("engine.system_b.pipeline.run_fingerprint_call", side_effect=_fp_legacy), \
         patch("engine.system_b.pipeline.run_verification_call", side_effect=_ver_legacy):
        pipeline = SystemBPipeline.__new__(SystemBPipeline)
        pipeline._config = PipelineConfig(enable_companion=True, enable_embeddings=False)
        pipeline._boundary = object()
        pipeline._companion_knowledge_graph = {"models": {}}
        pipeline._companion_reasoning_signals = {}
        pipeline._companion_relation_graph = {}
        pipeline._embedding_retriever = None
        pipeline._embedding_api_key = ""
        try:
            pipeline._run_companion(
                CritiqueRequest(query="legacy_q", vanilla_answer="legacy_va"),
                boundary_calls=[],
                conversation_context=ctx,
            )
        except _ShimDispatchedException:
            pass

    assert len(captured_ctx_fp) == 1
    assert captured_ctx_fp[0] is ctx
    assert captured_legacy_fp == [], "legacy fingerprint must not run when context present"


def test_run_companion_uses_legacy_path_when_no_context() -> None:
    """Without a ConversationContext, Lane 2 keeps using the legacy fingerprint path."""
    from engine.system_b.pipeline import PipelineConfig
    captured_ctx_fp: list = []
    captured_legacy_fp: list = []

    def _fp_ctx(*, context, client):  # noqa: ARG001
        captured_ctx_fp.append(context)
        raise _ShimDispatchedException()

    def _fp_legacy(*, query, vanilla_answer, client):  # noqa: ARG001
        captured_legacy_fp.append((query, vanilla_answer))
        raise _ShimDispatchedException()

    with patch("engine.system_b.pipeline.run_fingerprint_call_from_context", side_effect=_fp_ctx), \
         patch("engine.system_b.pipeline.run_fingerprint_call", side_effect=_fp_legacy):
        pipeline = SystemBPipeline.__new__(SystemBPipeline)
        pipeline._config = PipelineConfig(enable_companion=True, enable_embeddings=False)
        pipeline._boundary = object()
        pipeline._companion_knowledge_graph = {"models": {}}
        pipeline._companion_reasoning_signals = {}
        pipeline._companion_relation_graph = {}
        pipeline._embedding_retriever = None
        pipeline._embedding_api_key = ""
        try:
            pipeline._run_companion(
                CritiqueRequest(query="qtext", vanilla_answer="vatext"),
                boundary_calls=[],
                conversation_context=None,
            )
        except _ShimDispatchedException:
            pass

    assert captured_legacy_fp == [("qtext", "vatext")]
    assert captured_ctx_fp == [], "context fingerprint must not run when context is absent"


def test_run_companion_skips_both_paths_when_feature_disabled() -> None:
    """enable_companion=False short-circuits Lane 2 entirely."""
    from engine.system_b.pipeline import PipelineConfig
    pipeline = SystemBPipeline.__new__(SystemBPipeline)
    pipeline._config = PipelineConfig(enable_companion=False)
    pipeline._boundary = object()
    result = pipeline._run_companion(
        CritiqueRequest(query="q", vanilla_answer="a"),
        boundary_calls=[],
        conversation_context=_minimal_context(),
    )
    # CompanionRunResult with no card present
    assert result.companion_card is None
