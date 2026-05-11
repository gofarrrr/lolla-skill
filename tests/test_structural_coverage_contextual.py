"""Tests for the Lane 4 (Structural Coverage) packet- and IR-driven entry points.

Covers:
- `run_question_classification_from_packet` — classifies the 4 question
  types based on user-turn content; defaults on invalid output.
- `run_dimension_detection_from_packet` — reads both user and assistant
  turns as SOURCE; extractor summaries are CONTEXT only.
- `generate_gap_questions_from_packet` — no-op when no gap routes; builds
  a SOURCE-labelled user prompt when gaps exist.
- `run_structural_coverage_from_ir` — orchestrator delegates to the
  three packet-aware calls and reuses the routing + assembly.

Boundary calls are mocked; no real LLM work.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.boundary_provider import BoundaryCallMetadata
from engine.system_b.conversation_context import (
    ConversationContext,
    ExtractionPayload,
    LiveConstraint,
    Turn,
)
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.packet_builders.lane4 import Lane4Packet, build_lane4_packet
from engine.system_b.structural_coverage import (
    DimensionRoute,
    _DIMENSION_DETECTION_SYSTEM_FROM_CONTEXT,
    _QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT,
    _format_classification_from_packet_user_prompt,
    _format_dimension_detection_from_packet_user_prompt,
    _format_gap_question_from_packet_user_prompt,
    generate_gap_questions_from_packet,
    run_dimension_detection_from_packet,
    run_question_classification_from_packet,
    run_structural_coverage_from_ir,
    run_structural_coverage_with_traces_from_ir,
)


def _ext(
    *,
    decision_situation: str = "Should I take the offer?",
    original_framing: str = "Is this obvious or crazy?",
    constraints: tuple[LiveConstraint, ...] = (),
) -> ExtractionPayload:
    return ExtractionPayload(
        decision_situation=decision_situation,
        live_constraints=constraints,
        synthesized_position="",
        reasoning_passages=(),
        original_framing=original_framing,
        dropped_threads=(),
    )


def _ctx(turns: tuple[tuple[int, str, str], ...], **ext_kwargs) -> ConversationContext:
    return ConversationContext(
        turns=tuple(Turn(turn_index=i, speaker=s, text=t) for (i, s, t) in turns),
        extraction=_ext(**ext_kwargs),
    )


def _packet_from_ctx(ctx: ConversationContext) -> Lane4Packet:
    return build_lane4_packet(construct_conversation_ir(ctx))


def _boundary_returning(payload: dict) -> MagicMock:
    boundary = MagicMock()
    boundary.run_json = MagicMock(return_value=payload)
    return boundary


class _MetadataBoundary:
    def __init__(self, payloads: list[dict]) -> None:
        self._payloads = iter(payloads)
        self.call_count = 0
        self.last_call_metadata = BoundaryCallMetadata()

    def run_json(self, system_prompt: str, user_prompt: str) -> dict:  # noqa: ARG002
        self.call_count += 1
        self.last_call_metadata = BoundaryCallMetadata(
            provider_name="test-provider",
            model="test-model",
            status="ok",
            raw_message_content=f"payload-{self.call_count}",
            prompt_tokens=self.call_count,
            completion_tokens=self.call_count * 10,
            total_tokens=self.call_count * 11,
        )
        return next(self._payloads)


def _minimal_routing() -> dict:
    return {
        "dimensions": {
            "resource_allocation": {
                "dimension_name": "Resource Allocation",
                "cleaving_frame": "Supply vs Demand",
                "detect_when": ["allocation decisions are discussed"],
                "coverage_signals": ["trade-offs between competing uses"],
                "materiality_test": "would change the recommendation if analyzed",
                "question_types": ["decision-evaluation"],
                "models": ["opportunity-cost", "second-order-thinking"],
            },
            "commitment_reversibility": {
                "dimension_name": "Commitment & Reversibility",
                "cleaving_frame": "Lock-in vs Optionality",
                "detect_when": ["multi-year or hard-to-reverse moves"],
                "coverage_signals": ["exit costs analyzed"],
                "materiality_test": "lock-in could reverse the call",
                "question_types": ["decision-evaluation"],
                "models": ["optionality", "sunk-cost-fallacy"],
            },
        },
    }


# ---------- question classification ----------


def test_run_question_classification_from_packet_returns_valid_type() -> None:
    packet = _packet_from_ctx(_ctx(((1, "user", "Should I take this role?"), (1, "assistant", "Let's see."))))
    boundary = _boundary_returning({"question_type": "decision-evaluation"})
    assert run_question_classification_from_packet(boundary, packet) == "decision-evaluation"


def test_run_question_classification_from_packet_defaults_on_invalid_type() -> None:
    packet = _packet_from_ctx(_ctx(((1, "user", "X"), (1, "assistant", "Y"))))
    boundary = _boundary_returning({"question_type": "garbage"})
    assert run_question_classification_from_packet(boundary, packet) == "decision-evaluation"


def test_run_question_classification_from_packet_calls_boundary_with_context_prompt() -> None:
    packet = _packet_from_ctx(_ctx(((1, "user", "q1"), (1, "assistant", "a1"), (2, "user", "q2"))))
    boundary = _boundary_returning({"question_type": "action-planning"})
    run_question_classification_from_packet(boundary, packet)
    args, _ = boundary.run_json.call_args
    system_prompt, user_prompt = args
    assert system_prompt is _QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT
    assert "CONTEXT (scaffolding" in user_prompt
    assert "SOURCE (the user's actual turns" in user_prompt
    # SOURCE contains user turns, not assistant turns
    src_section = user_prompt.split("SOURCE", 1)[1]
    assert "q1" in src_section
    assert "q2" in src_section
    assert "a1" not in src_section


def test_format_classification_user_prompt_renders_context_before_source() -> None:
    packet = _packet_from_ctx(_ctx(
        ((1, "user", "user-turn-1"), (1, "assistant", "assistant-reply")),
        decision_situation="D",
        original_framing="F",
    ))
    prompt = _format_classification_from_packet_user_prompt(packet)
    # Ordering: CONTEXT first, then SOURCE
    assert prompt.index("CONTEXT") < prompt.index("SOURCE")
    # CONTEXT holds extractor summaries
    ctx_block, src_block = prompt.split("SOURCE", 1)
    assert "Decision situation: D" in ctx_block
    assert "Framing extracted upstream: F" in ctx_block
    # Assistant reply appears in CONTEXT (as scaffolding), not SOURCE
    assert "assistant-reply" in ctx_block
    assert "assistant-reply" not in src_block
    # User turn appears in SOURCE
    assert "user-turn-1" in src_block


# ---------- dimension detection ----------


def test_run_dimension_detection_from_packet_parses_output() -> None:
    packet = _packet_from_ctx(_ctx(((1, "user", "q"), (1, "assistant", "a"))))
    boundary = _boundary_returning({
        "dimensions": [
            {
                "dimension_id": "resource_allocation",
                "dimension_name": "Resource Allocation",
                "covered": False,
                "coverage_evidence": "Answer never analyses opportunity cost.",
                "materiality_note": "Could change the recommendation.",
            }
        ],
    })
    dims = run_dimension_detection_from_packet(
        boundary, packet, "decision-evaluation", _minimal_routing(),
    )
    assert len(dims) == 1
    assert dims[0].dimension_id == "resource_allocation"
    assert dims[0].covered is False


def test_run_dimension_detection_from_packet_calls_boundary_with_context_system_prompt() -> None:
    packet = _packet_from_ctx(_ctx(((1, "user", "user-q"), (1, "assistant", "assistant-a"))))
    boundary = _boundary_returning({"dimensions": []})
    run_dimension_detection_from_packet(
        boundary, packet, "decision-evaluation", _minimal_routing(),
    )
    args, _ = boundary.run_json.call_args
    system_prompt, user_prompt = args
    assert system_prompt is _DIMENSION_DETECTION_SYSTEM_FROM_CONTEXT
    assert "CONTEXT (scaffolding" in user_prompt
    # Both user and assistant turns go in SOURCE for detection (user for
    # detect_when conditions, assistant for coverage signals)
    src_section = user_prompt.split("SOURCE", 1)[1]
    assert "user-q" in src_section
    assert "assistant-a" in src_section


def test_format_dimension_detection_user_prompt_includes_catalog_and_question_type() -> None:
    packet = _packet_from_ctx(_ctx(((1, "user", "q"), (1, "assistant", "a"))))
    prompt = _format_dimension_detection_from_packet_user_prompt(
        packet, "causal-diagnosis", "CATALOG TEXT HERE",
    )
    assert "QUESTION TYPE: causal-diagnosis" in prompt
    assert "CATALOG TEXT HERE" in prompt


# ---------- gap question generation ----------


def test_generate_gap_questions_from_packet_returns_empty_when_no_routes() -> None:
    packet = _packet_from_ctx(_ctx(((1, "user", "q"), (1, "assistant", "a"))))
    boundary = _boundary_returning({})  # should never be called
    result = generate_gap_questions_from_packet(
        boundary, packet, "decision-evaluation", (), _minimal_routing(),
    )
    assert result == ()
    assert not boundary.run_json.called


def test_generate_gap_questions_from_packet_produces_questions_for_routes() -> None:
    packet = _packet_from_ctx(_ctx(((1, "user", "q"), (1, "assistant", "a"))))
    routes = (
        DimensionRoute(
            dimension_id="resource_allocation",
            dimension_name="Resource Allocation",
            candidate_model_ids=("opportunity-cost",),
            excluded_model_ids=(),
        ),
    )
    boundary = _boundary_returning({
        "gap_questions": {
            "resource_allocation": [
                "What are you giving up to make this investment?",
                "What would make the alternative more attractive than this?",
            ],
        },
    })
    result = generate_gap_questions_from_packet(
        boundary, packet, "decision-evaluation", routes, _minimal_routing(),
    )
    assert len(result) == 1
    assert result[0].dimension_id == "resource_allocation"
    assert len(result[0].questions) == 2


def test_format_gap_question_prompt_labels_context_vs_source() -> None:
    packet = _packet_from_ctx(_ctx(
        ((1, "user", "real user text here"), (1, "assistant", "assistant reply text")),
        decision_situation="summarized decision",
    ))
    routes = (
        DimensionRoute(
            dimension_id="resource_allocation",
            dimension_name="Resource Allocation",
            candidate_model_ids=("opportunity-cost",),
            excluded_model_ids=(),
        ),
    )
    prompt = _format_gap_question_from_packet_user_prompt(
        packet, "decision-evaluation", routes, _minimal_routing(),
    )
    assert "CONTEXT (scaffolding" in prompt
    assert "SOURCE (the real conversation" in prompt
    # User + assistant turns both in SOURCE (gap generator needs full context
    # to produce problem-specific questions)
    src_section = prompt.split("SOURCE", 1)[1]
    assert "real user text here" in src_section
    assert "assistant reply text" in src_section
    # Extractor summary lives in CONTEXT
    ctx_section = prompt.split("SOURCE", 1)[0]
    assert "summarized decision" in ctx_section
    # Gap section appears
    assert "GAP DIMENSION: Resource Allocation" in prompt


# ---------- orchestrator (run_structural_coverage_from_ir) ----------


def test_run_structural_coverage_from_ir_orchestrates_three_calls() -> None:
    """The orchestrator wires classification -> detection -> gap gen correctly."""
    ctx = _ctx(((1, "user", "should I?"), (1, "assistant", "maybe.")))
    ir = construct_conversation_ir(ctx)

    # Sequence: classification, detection, gap_questions — 3 calls
    call_payloads = iter([
        {"question_type": "decision-evaluation"},
        {"dimensions": [
            {
                "dimension_id": "resource_allocation",
                "dimension_name": "Resource Allocation",
                "covered": False,
                "coverage_evidence": "not addressed",
                "materiality_note": "material",
            },
        ]},
        {"gap_questions": {"resource_allocation": ["What would you give up?"]}},
    ])
    boundary = MagicMock()
    boundary.run_json = MagicMock(side_effect=lambda *args, **kwargs: next(call_payloads))

    card = run_structural_coverage_from_ir(
        boundary, ir, _minimal_routing(), anti_echo_model_ids=set(),
    )
    assert card is not None
    assert card.question_type == "decision-evaluation"
    assert len(card.dimensions) == 1
    assert len(card.gap_routes) == 1
    assert len(card.gap_questions) == 1
    # Boundary called exactly 3 times (classify + detect + gap)
    assert boundary.run_json.call_count == 3


def test_run_structural_coverage_with_traces_records_three_distinct_call_stages() -> None:
    """Trace-returning orchestrator captures each Lane 4 call immediately."""
    ctx = _ctx(((1, "user", "should I?"), (1, "assistant", "maybe.")))
    ir = construct_conversation_ir(ctx)
    boundary = _MetadataBoundary([
        {"question_type": "decision-evaluation"},
        {"dimensions": [
            {
                "dimension_id": "resource_allocation",
                "dimension_name": "Resource Allocation",
                "covered": False,
                "coverage_evidence": "not addressed",
                "materiality_note": "material",
            },
        ]},
        {"gap_questions": {"resource_allocation": ["What would you give up?"]}},
    ])

    result = run_structural_coverage_with_traces_from_ir(
        boundary, ir, _minimal_routing(), anti_echo_model_ids=set(),
    )

    assert result.card is not None
    assert [trace.stage for trace in result.boundary_calls] == [
        "structural_coverage_classification",
        "structural_coverage_detection",
        "structural_coverage_gap_questions",
    ]
    assert [trace.raw_message_content for trace in result.boundary_calls] == [
        "payload-1",
        "payload-2",
        "payload-3",
    ]
    assert [trace.total_tokens for trace in result.boundary_calls] == [11, 22, 33]


def test_run_structural_coverage_from_ir_skips_gap_gen_when_no_gaps() -> None:
    """When no dimensions are uncovered, gap question generation is skipped."""
    ctx = _ctx(((1, "user", "q"), (1, "assistant", "a")))
    ir = construct_conversation_ir(ctx)
    call_payloads = iter([
        {"question_type": "decision-evaluation"},
        {"dimensions": []},  # no gaps
    ])
    boundary = MagicMock()
    boundary.run_json = MagicMock(side_effect=lambda *args, **kwargs: next(call_payloads))

    card = run_structural_coverage_from_ir(
        boundary, ir, _minimal_routing(), anti_echo_model_ids=set(),
    )
    assert card is not None
    assert card.gap_questions == ()
    # Only 2 boundary calls (no gap gen)
    assert boundary.run_json.call_count == 2


def test_run_structural_coverage_with_traces_records_two_distinct_call_stages_without_gaps() -> None:
    """When there are no gap routes, no gap-question trace should be fabricated."""
    ctx = _ctx(((1, "user", "q"), (1, "assistant", "a")))
    ir = construct_conversation_ir(ctx)
    boundary = _MetadataBoundary([
        {"question_type": "decision-evaluation"},
        {"dimensions": []},
    ])

    result = run_structural_coverage_with_traces_from_ir(
        boundary, ir, _minimal_routing(), anti_echo_model_ids=set(),
    )

    assert result.card is not None
    assert result.card.gap_questions == ()
    assert [trace.stage for trace in result.boundary_calls] == [
        "structural_coverage_classification",
        "structural_coverage_detection",
    ]
    assert [trace.raw_message_content for trace in result.boundary_calls] == [
        "payload-1",
        "payload-2",
    ]


def test_run_structural_coverage_from_ir_returns_none_on_classification_failure() -> None:
    ctx = _ctx(((1, "user", "q"), (1, "assistant", "a")))
    ir = construct_conversation_ir(ctx)
    boundary = MagicMock()
    boundary.run_json = MagicMock(side_effect=RuntimeError("network down"))
    result = run_structural_coverage_from_ir(
        boundary, ir, _minimal_routing(), anti_echo_model_ids=set(),
    )
    assert result is None


def test_run_structural_coverage_from_ir_applies_anti_echo() -> None:
    """Anti-echo exclusion should pass through to route_gap_dimensions."""
    ctx = _ctx(((1, "user", "q"), (1, "assistant", "a")))
    ir = construct_conversation_ir(ctx)
    call_payloads = iter([
        {"question_type": "decision-evaluation"},
        {"dimensions": [
            {
                "dimension_id": "resource_allocation",
                "dimension_name": "Resource Allocation",
                "covered": False,
                "coverage_evidence": "missing",
                "materiality_note": "material",
            },
        ]},
        {"gap_questions": {"resource_allocation": ["q?"]}},
    ])
    boundary = MagicMock()
    boundary.run_json = MagicMock(side_effect=lambda *args, **kwargs: next(call_payloads))

    # Exclude one of the two candidate models for resource_allocation
    card = run_structural_coverage_from_ir(
        boundary, ir, _minimal_routing(),
        anti_echo_model_ids={"opportunity-cost"},
    )
    assert card is not None
    assert len(card.gap_routes) == 1
    route = card.gap_routes[0]
    assert "opportunity-cost" in route.excluded_model_ids
    assert "opportunity-cost" not in route.candidate_model_ids
    assert "second-order-thinking" in route.candidate_model_ids


def test_system_prompts_explicitly_label_context_vs_source() -> None:
    """Anti-regression: the Phase 2a lesson (explicit CONTEXT/SOURCE distinction
    with do-not-quote language) is baked into both new system prompts."""
    for name, prompt in (
        ("classification", _QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT),
        ("detection", _DIMENSION_DETECTION_SYSTEM_FROM_CONTEXT),
    ):
        assert "CONTEXT" in prompt, f"{name} prompt missing CONTEXT label"
        assert "SOURCE" in prompt, f"{name} prompt missing SOURCE label"


def test_format_classification_packet_prompt_with_active_constraints() -> None:
    """Realistic Lane 4 prompt with active constraints renders cleanly."""
    ctx = ConversationContext(
        turns=(
            Turn(turn_index=1, speaker="user", text="I have 8 months runway. Plan to launch in 6 weeks."),
            Turn(turn_index=1, speaker="assistant", text="Tell me about your pipeline."),
            Turn(turn_index=2, speaker="user", text="4-5 informal conversations. None committed."),
        ),
        extraction=ExtractionPayload(
            decision_situation="Whether the user should launch in 6 weeks or delay.",
            live_constraints=(
                LiveConstraint(
                    constraint="Pipeline: 4-5 informal network conversations, no signed commitments",
                    introduced_turn=1,
                    status="active",
                    weight="structural",
                ),
                LiveConstraint(
                    constraint="Runway: 8 months at zero revenue",
                    introduced_turn=1,
                    status="active",
                    weight="structural",
                ),
            ),
            synthesized_position="",
            reasoning_passages=(),
            original_framing="User seeks tactical launch plan starting in 6 weeks.",
            dropped_threads=(),
        ),
    )
    packet = _packet_from_ctx(ctx)

    classify_prompt = _format_classification_from_packet_user_prompt(packet)
    assert "Decision situation: Whether the user should launch in 6 weeks" in classify_prompt
    # Classification CONTEXT does not render constraints (matches old shape)
    detect_prompt = _format_dimension_detection_from_packet_user_prompt(
        packet, "decision-evaluation", "(test catalog)",
    )
    # Detection CONTEXT renders constraints with [ACTIVE] tag (no weight in IR)
    assert "[ACTIVE] Pipeline: 4-5 informal network conversations" in detect_prompt
    assert "[ACTIVE] Runway: 8 months at zero revenue" in detect_prompt
