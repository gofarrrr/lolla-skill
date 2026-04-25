"""Structural Coverage Lane (Lane 4): MECE dimension detection, coverage gap mapping,
gap question generation.

This module implements the Structural Coverage lane, which decomposes a problem
into structural dimensions, checks which ones the vanilla answer addressed,
bridges each uncovered dimension to relevant mental models, and generates
discovery questions for each gap (the HITL bridge).

Unlike Lanes 1-3 which work reactively (from what's in the answer or question),
Lane 4 works proactively — from the problem's shape — to find dimensions the
answer didn't address at all.

The entire lane is gated on ``PipelineConfig.enable_structural_coverage``.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Protocol

from .boundary_validation import coerce_str
from .conversation_context import ConversationContext
from .ir import ConversationIR
from .packet_builders.lane4 import Lane4Packet, build_lane4_packet

_LOGGER = logging.getLogger("system_b.structural_coverage")


# ---------------------------------------------------------------------------
# Public dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DetectedDimension:
    """A structural dimension detected in the problem."""

    dimension_id: str
    dimension_name: str
    covered: bool
    coverage_evidence: str  # what in the answer addresses this, or why it's absent
    materiality_note: str  # the "so what" for this gap


@dataclass(frozen=True)
class DimensionRoute:
    """Deterministic routing result for one uncovered dimension."""

    dimension_id: str
    dimension_name: str
    candidate_model_ids: tuple[str, ...]  # after anti-echo exclusion
    excluded_model_ids: tuple[str, ...]  # models excluded by anti-echo


@dataclass(frozen=True)
class GapQuestion:
    """Discovery questions for one uncovered structural dimension."""

    dimension_id: str
    dimension_name: str
    questions: tuple[str, ...]  # 2-3 discovery questions


@dataclass(frozen=True)
class StructuralCoverageCard:
    """The output artifact of the Structural Coverage lane."""

    question_type: str = ""
    dimensions: tuple[DetectedDimension, ...] = ()
    gap_routes: tuple[DimensionRoute, ...] = ()
    gap_questions: tuple[GapQuestion, ...] = ()
    anti_echo_model_ids: tuple[str, ...] = ()

    def to_payload(self) -> dict:
        """Serialize to JSON-compatible dict for Observatory / eval surfaces."""
        return {
            "question_type": self.question_type,
            "dimensions": [
                {
                    "dimension_id": d.dimension_id,
                    "dimension_name": d.dimension_name,
                    "covered": d.covered,
                    "coverage_evidence": d.coverage_evidence,
                    "materiality_note": d.materiality_note,
                }
                for d in self.dimensions
            ],
            "gap_routes": [
                {
                    "dimension_id": r.dimension_id,
                    "dimension_name": r.dimension_name,
                    "candidate_model_ids": list(r.candidate_model_ids),
                    "excluded_model_ids": list(r.excluded_model_ids),
                }
                for r in self.gap_routes
            ],
            "gap_questions": [
                {
                    "dimension_id": gq.dimension_id,
                    "dimension_name": gq.dimension_name,
                    "questions": list(gq.questions),
                }
                for gq in self.gap_questions
            ],
            "anti_echo_model_ids": list(self.anti_echo_model_ids),
        }

    @classmethod
    def from_payload(cls, data: dict) -> "StructuralCoverageCard":
        """Deserialize from a JSON-compatible dict."""
        dimensions = tuple(
            DetectedDimension(
                dimension_id=d.get("dimension_id", ""),
                dimension_name=d.get("dimension_name", ""),
                covered=bool(d.get("covered", True)),
                coverage_evidence=d.get("coverage_evidence", ""),
                materiality_note=d.get("materiality_note", ""),
            )
            for d in data.get("dimensions", [])
        )
        gap_routes = tuple(
            DimensionRoute(
                dimension_id=r.get("dimension_id", ""),
                dimension_name=r.get("dimension_name", ""),
                candidate_model_ids=tuple(r.get("candidate_model_ids", [])),
                excluded_model_ids=tuple(r.get("excluded_model_ids", [])),
            )
            for r in data.get("gap_routes", [])
        )
        gap_questions = tuple(
            GapQuestion(
                dimension_id=gq.get("dimension_id", ""),
                dimension_name=gq.get("dimension_name", ""),
                questions=tuple(gq.get("questions", [])),
            )
            for gq in data.get("gap_questions", [])
        )
        return cls(
            question_type=data.get("question_type", ""),
            dimensions=dimensions,
            gap_routes=gap_routes,
            gap_questions=gap_questions,
            anti_echo_model_ids=tuple(data.get("anti_echo_model_ids", [])),
        )


# ---------------------------------------------------------------------------
# Boundary protocol
# ---------------------------------------------------------------------------

class _BoundaryClient(Protocol):
    def run_json(self, system_prompt: str, user_prompt: str) -> dict: ...


# ---------------------------------------------------------------------------
# LLM Boundary Call 1: Question Classification
# ---------------------------------------------------------------------------

_VALID_QUESTION_TYPES = frozenset({
    "causal-diagnosis",
    "decision-evaluation",
    "action-planning",
    "prediction",
})


# ---------------------------------------------------------------------------
# Phase 2b: Conversation-first question classification
# ---------------------------------------------------------------------------
#
# Separate system prompt so the legacy path's calibration (reads "QUESTION" as
# the collapsed decision_situation paraphrase) stays stable while the new path
# explicitly tells the LLM to classify based on the user's actual turns.
#
# Note: Lane 4 has no evidence-substring validation downstream (unlike Lane 3).
# The CONTEXT/SOURCE split here is prompt guidance — steering the LLM to treat
# user turns as primary truth — not a mechanical output validator. Quality
# signal is observed via classification stability and dimension-detection
# shifts across paths, not via drop rates.

_QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT = """\
You are a question classifier. Your job is to read a CONVERSATION (user turns \
plus assistant replies) and classify the QUESTION the user is posing into \
exactly one of four structural types, based on what kind of answer the \
question demands.

The user prompt has two sections:
  - CONTEXT: extractor summaries (decision_situation, original_framing, \
constraints, dropped threads, assistant replies). These are secondary \
scaffolding for understanding. Classify based on what the USER actually asked, \
not on the extractor's paraphrase.
  - SOURCE: the user's actual turns. The first user turn is the canonical \
anchor for the question.

The four types:
  - "causal-diagnosis" — The user asks WHY something happened or is happening. \
Demands root-cause reasoning. Examples: "Why are sales down?", \
"What's causing the high churn rate?"
  - "decision-evaluation" — The user asks WHETHER to do something. \
Demands trade-off and commitment reasoning. Examples: "Should we sign \
the deal?", "Is it worth expanding into Europe?"
  - "action-planning" — The user asks HOW to do something. \
Demands sequencing and execution reasoning. The decision is already made; \
the question is about implementation. Examples: "How do we restructure \
the engineering org?", "What's the plan for the product launch?"
  - "prediction" — The user asks WHAT WILL HAPPEN. Demands forecasting \
and scenario reasoning. Examples: "What happens if we raise prices 20%?", \
"Where will the market be in 3 years?"

Return a JSON object: {"question_type": "<type>"}

Rules:
- Pick the DOMINANT type. Many questions blend types — choose the one that \
best captures what kind of reasoning the answer needs.
- If the user's framing is ambiguous, default to "decision-evaluation" — most \
strategic questions are fundamentally about whether to act.
- Classify the USER'S question (primarily the first user turn, refined by \
subsequent user turns if they sharpen the framing). Do not classify the \
CONTEXT summary if it diverges from what the user actually said.
- Return ONLY the JSON object. No explanation.
"""


def _format_classification_from_context_user_prompt(context: ConversationContext) -> str:
    """User-prompt body for context-first question classification.

    CONTEXT section holds extractor summaries + assistant replies (scaffolding).
    SOURCE section holds user turns verbatim — the primary signal.
    """
    ext = context.extraction
    parts: list[str] = ["CONTEXT (scaffolding — classify the user's actual question, not this summary):"]
    if ext.decision_situation:
        parts.append(f"- Decision situation: {ext.decision_situation}")
    if ext.original_framing:
        parts.append(f"- Framing extracted upstream: {ext.original_framing}")

    assistant_turns = [t for t in context.turns if t.speaker == "assistant"]
    if assistant_turns:
        parts.append("- Assistant replies (context for what the user was engaging with):")
        for t in assistant_turns:
            parts.append(f"  [Turn {t.turn_index} ASSISTANT] {t.text[:500]}")

    parts.append("")
    parts.append("SOURCE (the user's actual turns — first user turn is the canonical question anchor):")
    for t in context.turns:
        if t.speaker == "user":
            parts.append(f"[Turn {t.turn_index}] USER:")
            parts.append(t.text)
            parts.append("")

    return "\n".join(parts)


def run_question_classification_from_context(
    boundary: _BoundaryClient,
    context: ConversationContext,
) -> str:
    """Conversation-first entry point for question classification — Phase 2b."""
    user_prompt = _format_classification_from_context_user_prompt(context)
    raw = boundary.run_json(_QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT, user_prompt)
    qtype = coerce_str(raw.get("question_type", ""))
    if qtype not in _VALID_QUESTION_TYPES:
        _LOGGER.warning("Invalid question_type %r, defaulting to decision-evaluation", qtype)
        qtype = "decision-evaluation"
    return qtype


# ---------------------------------------------------------------------------
# LLM Boundary Call 2: Dimension Detection + Coverage Check
# ---------------------------------------------------------------------------

def _build_dimension_catalog_text(dimension_routing: dict) -> str:
    """Format the dimension catalog for injection into the detection prompt."""
    dims = dimension_routing.get("dimensions", {})
    lines: list[str] = []
    for dim_id, dim in sorted(dims.items()):
        lines.append(f"## {dim['dimension_name']} (id: {dim_id})")
        lines.append(f"Cleaving frame: {dim.get('cleaving_frame', '')}")
        lines.append("Detect when:")
        for cond in dim.get("detect_when", []):
            lines.append(f"  - {cond}")
        lines.append("Coverage signals (what 'addressing this' looks like):")
        for sig in dim.get("coverage_signals", []):
            lines.append(f"  - {sig}")
        lines.append(f"Materiality test: {dim.get('materiality_test', '')}")
        lines.append(f"Applicable question types: {', '.join(dim.get('question_types', []))}")
        lines.append("")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Phase 2b: Conversation-first dimension detection
# ---------------------------------------------------------------------------
#
# Detection has two legitimate evidence sources: user turns (for what the
# question establishes — detect_when conditions are about the QUESTION) and
# assistant replies (for what the answer addressed — coverage is about the
# ANSWER). Both go in the SOURCE section with labels; only extractor summaries
# live in CONTEXT.

_DIMENSION_DETECTION_SYSTEM_FROM_CONTEXT = """\
You are a structural coverage analyst. Your job is to read a CONVERSATION \
(user turns plus assistant replies) and determine which structural dimensions \
of the problem are present and whether the answer addresses each one.

The user prompt has two sections:
  - CONTEXT: extractor summaries (decision_situation, framing, constraints, \
dropped threads). These are scaffolding for understanding the decision. \
They are NOT the primary source of truth for what the user asked or what the \
assistant answered. Do not base detection or coverage on paraphrased summaries.
  - SOURCE: the actual conversation, turn by turn. User turns establish the \
question (detect_when conditions are about what the user asked). Assistant \
turns establish the answer (coverage is about what was addressed). Both are \
legitimate evidence sources for this lane.

You will receive:
1. The question type (causal-diagnosis, decision-evaluation, action-planning, prediction)
2. A catalog of 15 structural dimensions with detect_when conditions and coverage signals
3. CONTEXT + SOURCE (as described above)

Your task:
1. DETECT: Which dimensions are structurally present in this problem? Use the \
detect_when conditions. A dimension is present if at least 1 of its detect_when \
conditions is clearly met by the USER'S QUESTION (SOURCE — user turns, primarily \
the first). Only consider dimensions whose question_types include the classified \
question type. Think broadly — typically 6-10 dimensions fire for a strategic question.
2. ASSESS COVERAGE: For each detected dimension, does the ANSWER (SOURCE — \
assistant turns) engage with the structural tension described by the dimension's \
cleaving frame? A dimension is "covered" ONLY if the assistant's replies:
  (a) explicitly identify the tension or trade-off described by the cleaving frame, AND
  (b) reason through both sides of that tension (not just one), AND
  (c) reach or recommend a position on how to resolve it.
If the assistant merely MENTIONS a related topic, uses a KEYWORD associated with \
the dimension, or ACKNOWLEDGES that the issue exists without analyzing it — \
that is NOT coverage. Coverage requires analytical depth, not topic presence. \
Coverage evidence you cite should be recognizable to the user/reviewer as \
something the assistant actually said.
3. MATERIALITY RANKING: After coverage assessment, RANK all uncovered dimensions \
by materiality — how likely is it that analyzing this dimension would REVERSE \
or SUBSTANTIALLY ALTER the recommendation? Then keep ONLY the top 3-5 as gaps. \
Mark the rest as covered with coverage_evidence: "Immaterial: [reason]".

Return a JSON object:
{
  "dimensions": [
    {
      "dimension_id": "<id from catalog>",
      "dimension_name": "<name from catalog>",
      "covered": true/false,
      "coverage_evidence": "<what in the assistant's replies addresses this, OR what's missing>",
      "materiality_note": "<why this gap matters for the decision, or 'covered'/'immaterial'>"
    }
  ]
}

HARD CONSTRAINT: Maximum 5 dimensions with covered=false. If your initial \
assessment yields more than 5 gaps, you MUST demote the least material ones \
to covered. This is not optional.

Rules:
- Return ONLY dimensions that are structurally present (6-10 typical).
- Maximum 5 gaps. Typical is 2-4. A gap must be able to CHANGE the recommendation.
- Mentioning is not covering. For every dimension, test: "Does the assistant \
reason through BOTH SIDES of this dimension's cleaving frame?" Examples:
  * Stakeholder Alignment: Discussing people is NOT coverage. Requires: who \
APPROVES, who BLOCKS, influence strategy.
  * Timing & Sequencing: Listing timeframes is NOT coverage. Requires: why \
this ORDER, critical path, delay impact.
  * Commitment & Reversibility: Proposing terms is NOT coverage. Requires: \
EXIT costs, lock-in, optionality consumed.
  * Uncertainty Type: Presenting numbers is NOT coverage. Requires: what is \
KNOWABLE vs genuinely UNKNOWABLE.
  * Information Quality: Adjusting for risks is NOT coverage. Requires: \
questioning data RELIABILITY, missing evidence.
  * Competitive Dynamics: Mentioning competitors is NOT coverage. Requires: \
modeling how they RESPOND.
  * Resource Allocation: Stating budget is NOT coverage. Requires: what you \
GIVE UP and why this beats alternatives.
  * Scaling Dynamics: Mentioning growth is NOT coverage. Requires: what \
BREAKS or CHANGES at scale.
  * Incentive Alignment: Listing parties is NOT coverage. Requires: where \
incentives DIVERGE and realignment mechanism.
  * Feedback & System Dynamics: Describing cause-effect is NOT coverage. \
Requires: identifying FEEDBACK LOOPS.
- Coverage evidence should quote or paraphrase assistant-turn content. Do NOT \
cite extractor summaries from CONTEXT as coverage evidence.

CHECKLIST — COMMONLY-MISSED DIMENSIONS:
When reading the conversation turn-by-turn, dimensions that are IMPLICIT in \
the user's framing (rather than verbatim keywords) can get deprioritized. \
Before finalizing your dimension list, explicitly verify you have considered \
each of the following — they apply to most strategic questions and are the \
most common miss-mode for this lane:

- Timing & Sequencing: ANY deadline, time pressure, or sequencing constraint \
in the user's turns (even mentioned briefly — e.g. "I have 7 days", "by end \
of semester", "before renewal") → DETECT this dimension.
- Uncertainty Type: ANY probabilistic or unpredictable element in the \
decision (market reactions, other parties' behavior, future outcomes the \
user cannot know from current evidence) → DETECT.
- Competitive Dynamics: ANY external party that might respond to this \
decision (competitors, alternatives, other candidates, collaborators who \
could defect) → DETECT.
- Risk Response: ANY material downside or what-if concern the user has \
raised (financial, career, relational, reputational) → DETECT.

These dimensions are LOW BAR for detection (if the detect_when trigger fires, \
include them) and HIGH BAR for coverage (mark covered ONLY if the assistant's \
replies reason through both sides of the tension). Missing them is a failure \
mode; false-positive detection is easier to correct via materiality demotion \
than false-negative omission.

- Return ONLY the JSON object. No explanation.
"""


def _format_dimension_detection_from_context_user_prompt(
    context: ConversationContext,
    question_type: str,
    dimension_catalog_text: str,
) -> str:
    """User-prompt body for context-first dimension detection.

    CONTEXT holds extractor summaries; SOURCE holds the full turn-by-turn
    conversation with user and assistant turns clearly labelled so the LLM
    can cite either side when judging coverage.
    """
    ext = context.extraction
    parts: list[str] = [
        f"QUESTION TYPE: {question_type}",
        "",
        f"DIMENSION CATALOG:",
        dimension_catalog_text,
        "",
        "CONTEXT (scaffolding — not the primary source of truth for detection or coverage):",
    ]
    if ext.decision_situation:
        parts.append(f"- Decision situation: {ext.decision_situation}")
    if ext.original_framing:
        parts.append(f"- Framing extracted upstream: {ext.original_framing}")
    if ext.live_constraints:
        parts.append("- Constraints:")
        for c in ext.live_constraints:
            status = c.status or "active"
            weight = c.weight or "situational"
            tag = status.upper() if status == "active" else f"{status.upper()}/{weight.upper()}"
            parts.append(f"  - [{tag}] {c.constraint} (turn {c.introduced_turn})")
    if ext.dropped_threads:
        parts.append("- Dropped threads:")
        for d in ext.dropped_threads:
            line = (
                f"  - {d.thread} (raised by {d.raised_by or '?'} turn {d.raised_turn}, "
                f"status: {d.status or '?'})"
            )
            if d.superseded_by:
                line += f", superseded_by: {d.superseded_by}"
            parts.append(line)

    parts.append("")
    parts.append("SOURCE (primary — USER turns establish the question for detection; ASSISTANT turns establish the answer for coverage):")
    for t in context.turns:
        parts.append(f"[Turn {t.turn_index}] {t.speaker.upper()}:")
        parts.append(t.text)
        parts.append("")

    return "\n".join(parts)


def run_dimension_detection_from_context(
    boundary: _BoundaryClient,
    context: ConversationContext,
    question_type: str,
    structural_coverage_routing: dict,
) -> tuple[DetectedDimension, ...]:
    """Conversation-first dimension detection — Phase 2b."""
    catalog_text = _build_dimension_catalog_text(structural_coverage_routing)
    user_prompt = _format_dimension_detection_from_context_user_prompt(
        context, question_type, catalog_text,
    )
    raw = boundary.run_json(_DIMENSION_DETECTION_SYSTEM_FROM_CONTEXT, user_prompt)
    return _parse_dimension_detection(raw)


_MAX_GAPS = 5  # Hard cap — even if the LLM returns more, we truncate.


def _parse_dimension_detection(raw: dict) -> tuple[DetectedDimension, ...]:
    """Parse the LLM response into DetectedDimension objects.

    Enforces a hard cap of ``_MAX_GAPS`` uncovered dimensions.  If the LLM
    returns more, the excess gaps (ordered last in the response) are demoted
    to covered with an "Immaterial (demoted)" evidence note.
    """
    raw_dims = raw.get("dimensions", [])
    if not isinstance(raw_dims, list):
        _LOGGER.warning("dimension detection returned non-list, got %s", type(raw_dims).__name__)
        return ()

    dims: list[DetectedDimension] = []
    for d in raw_dims:
        if not isinstance(d, dict):
            continue
        dim_id = coerce_str(d.get("dimension_id", ""))
        if not dim_id:
            continue
        dims.append(DetectedDimension(
            dimension_id=dim_id,
            dimension_name=coerce_str(d.get("dimension_name", "")),
            covered=bool(d.get("covered", True)),
            coverage_evidence=coerce_str(d.get("coverage_evidence", "")),
            materiality_note=coerce_str(d.get("materiality_note", "")),
        ))

    # Enforce hard gap cap — demote excess gaps to covered
    gap_count = sum(1 for d in dims if not d.covered)
    if gap_count > _MAX_GAPS:
        _LOGGER.info(
            "Demoting %d excess gaps (LLM returned %d, cap is %d)",
            gap_count - _MAX_GAPS, gap_count, _MAX_GAPS,
        )
        # Keep the first _MAX_GAPS gaps; demote the rest (LLM puts most material first)
        seen_gaps = 0
        capped: list[DetectedDimension] = []
        for d in dims:
            if not d.covered:
                seen_gaps += 1
                if seen_gaps > _MAX_GAPS:
                    d = DetectedDimension(
                        dimension_id=d.dimension_id,
                        dimension_name=d.dimension_name,
                        covered=True,
                        coverage_evidence=f"Immaterial (demoted): {d.coverage_evidence}",
                        materiality_note=d.materiality_note,
                    )
            capped.append(d)
        dims = capped

    return tuple(dims)


# ---------------------------------------------------------------------------
# Gap question parsing
# ---------------------------------------------------------------------------

def _parse_gap_questions(raw) -> dict[str, tuple[str, ...]]:
    """Parse the LLM response into a dict of dimension_id → question tuples."""
    if not isinstance(raw, dict):
        return {}
    gq = raw.get("gap_questions")
    if not isinstance(gq, dict):
        return {}
    result: dict[str, tuple[str, ...]] = {}
    for dim_id, questions in gq.items():
        if not isinstance(dim_id, str) or not isinstance(questions, list):
            continue
        cleaned = tuple(coerce_str(q) for q in questions if isinstance(q, str) and q.strip())
        if cleaned:
            result[dim_id] = cleaned
    return result


# ---------------------------------------------------------------------------
# LLM Boundary Call 3: Gap Question Generation
# ---------------------------------------------------------------------------

_GAP_QUESTION_GENERATION_SYSTEM = """\
You are a discovery question generator. Your job is to produce 2-3 questions \
for each structural gap identified in a strategic answer. These questions ask \
for information that only the decision-maker has — they are never answered by \
an AI.

Question design rules:

1. **5Ws+H discovery sequence**: Start with concrete, factual questions \
(who, what, where, when), then move to reflective questions (why). \
"Why" comes last — it risks triggering defensiveness if asked too early.

2. **"What" and "Why" over "How"**: Ask for context, not solutions. \
"What are the constraints on this timeline?" not \
"How would you handle the timeline constraints?" \
Asking "how" shrinks the problem to mechanics. Asking "what" and "why" \
opens the problem space.

3. **Problem-specific**: Every question must reference the actual situation \
described in the query. Generic questions like "Who are the stakeholders?" \
are useless. Instead: "Who on the executive team has the most to lose if \
this deal falls through?"

4. **Plain language**: The structural dimension and bridged models inform \
the angle of the question, but neither dimension names nor model names \
appear in the questions themselves. The user should not need to know \
about the MECE framework to answer.

5. **Answerable by the decision-maker**: Every question must be one the \
person facing this decision can actually answer from their knowledge of \
the situation. No philosophical questions. No analytical questions an \
AI could answer. If the decision-maker can't answer it, it's not a \
discovery question.

6. **2-3 questions per gap**: More than 3 creates survey fatigue. Fewer \
than 2 doesn't explore the dimension. Each question should open a \
different angle on the gap.

Return a JSON object:
{
  "gap_questions": {
    "<dimension_id>": [
      "<question 1>",
      "<question 2>"
    ]
  }
}

Return ONLY the JSON object. No explanation.
"""




# ---------------------------------------------------------------------------
# Phase 2b: Conversation-first gap question generation
# ---------------------------------------------------------------------------
#
# Gap questions need to be problem-specific — they reference the actual
# situation so the decision-maker can answer them without reading an AI-facing
# spec. The CONTEXT/SOURCE split here steers the LLM to ground its question
# wording in the real conversation rather than in extractor paraphrases.

def _format_gap_question_from_context_user_prompt(
    context: ConversationContext,
    question_type: str,
    gap_routes: tuple[DimensionRoute, ...],
    structural_coverage_routing: dict,
) -> str:
    """User-prompt body for context-first gap question generation.

    CONTEXT: extractor summaries. SOURCE: full conversation (user + assistant
    turns). Questions generated should reference the conversation's real
    details — the kind of particulars the user would recognize as being about
    their situation, not the extractor's re-labelled framing.
    """
    routing_dims = structural_coverage_routing.get("dimensions", {})
    gap_sections: list[str] = []
    for route in gap_routes:
        dim_def = routing_dims.get(route.dimension_id, {})
        gap_sections.append(
            f"GAP DIMENSION: {route.dimension_name} (id: {route.dimension_id})\n"
            f"Cleaving frame: {dim_def.get('cleaving_frame', 'N/A')}\n"
            f"What's missing: The assistant did not address this dimension.\n"
            f"Why it matters: {dim_def.get('materiality_test', 'N/A')}"
        )

    ext = context.extraction
    parts: list[str] = [
        f"QUESTION TYPE: {question_type}",
        "",
        "CONTEXT (scaffolding — do NOT quote verbatim into your questions; use only for grounding):",
    ]
    if ext.decision_situation:
        parts.append(f"- Decision situation: {ext.decision_situation}")
    if ext.original_framing:
        parts.append(f"- Framing extracted upstream: {ext.original_framing}")
    if ext.live_constraints:
        parts.append("- Constraints:")
        for c in ext.live_constraints:
            status = c.status or "active"
            weight = c.weight or "situational"
            tag = status.upper() if status == "active" else f"{status.upper()}/{weight.upper()}"
            parts.append(f"  - [{tag}] {c.constraint} (turn {c.introduced_turn})")

    parts.append("")
    parts.append("SOURCE (the real conversation — your questions should reference particulars from here):")
    for t in context.turns:
        parts.append(f"[Turn {t.turn_index}] {t.speaker.upper()}:")
        parts.append(t.text)
        parts.append("")

    parts.append("")
    parts.append("STRUCTURAL GAPS:")
    parts.append("")
    parts.append("\n\n".join(gap_sections))

    return "\n".join(parts)


def generate_gap_questions_from_context(
    boundary: _BoundaryClient,
    context: ConversationContext,
    question_type: str,
    gap_routes: tuple[DimensionRoute, ...],
    structural_coverage_routing: dict,
) -> tuple[GapQuestion, ...]:
    """Conversation-first gap question generation — Phase 2b."""
    if not gap_routes:
        return ()

    user_prompt = _format_gap_question_from_context_user_prompt(
        context, question_type, gap_routes, structural_coverage_routing,
    )
    raw = boundary.run_json(_GAP_QUESTION_GENERATION_SYSTEM, user_prompt)
    parsed = _parse_gap_questions(raw)

    results: list[GapQuestion] = []
    for route in gap_routes:
        questions = parsed.get(route.dimension_id)
        if questions:
            results.append(GapQuestion(
                dimension_id=route.dimension_id,
                dimension_name=route.dimension_name,
                questions=questions,
            ))
    return tuple(results)


# ---------------------------------------------------------------------------
# Deterministic middle: Bridge + Anti-Echo
# ---------------------------------------------------------------------------

def route_gap_dimensions(
    dimensions: tuple[DetectedDimension, ...],
    structural_coverage_routing: dict,
    anti_echo_model_ids: set[str],
) -> tuple[DimensionRoute, ...]:
    """Route uncovered dimensions to candidate models via compiled KG.

    For each dimension where ``covered == False``:
    1. Look up ``models`` in structural_coverage_routing
    2. Exclude models in ``anti_echo_model_ids`` (from Lanes 1, 2, 3)
    3. Return DimensionRoute with candidates and excluded
    """
    routing_dims = structural_coverage_routing.get("dimensions", {})
    routes: list[DimensionRoute] = []

    for dim in dimensions:
        if dim.covered:
            continue

        dim_def = routing_dims.get(dim.dimension_id)
        if not dim_def:
            _LOGGER.warning("No routing definition for dimension %r", dim.dimension_id)
            continue

        all_models = dim_def.get("models", [])
        candidates = [m for m in all_models if m not in anti_echo_model_ids]
        excluded = [m for m in all_models if m in anti_echo_model_ids]

        if not candidates:
            _LOGGER.info(
                "All models for dimension %r excluded by anti-echo (%d models)",
                dim.dimension_id,
                len(all_models),
            )
            continue

        routes.append(DimensionRoute(
            dimension_id=dim.dimension_id,
            dimension_name=dim.dimension_name,
            candidate_model_ids=tuple(candidates),
            excluded_model_ids=tuple(excluded),
        ))

    return tuple(routes)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def assemble_structural_coverage_card(
    question_type: str,
    dimensions: tuple[DetectedDimension, ...],
    gap_routes: tuple[DimensionRoute, ...],
    anti_echo_model_ids: set[str],
    gap_questions: tuple[GapQuestion, ...] = (),
) -> StructuralCoverageCard:
    """Assemble all pieces into the frozen output card."""
    return StructuralCoverageCard(
        question_type=question_type,
        dimensions=dimensions,
        gap_routes=gap_routes,
        gap_questions=gap_questions,
        anti_echo_model_ids=tuple(sorted(anti_echo_model_ids)),
    )


# ---------------------------------------------------------------------------
# Public API — single entry point for pipeline.py
# ---------------------------------------------------------------------------

def run_structural_coverage_from_context(
    boundary: _BoundaryClient,
    context: ConversationContext,
    structural_coverage_routing: dict,
    anti_echo_model_ids: set[str],
) -> StructuralCoverageCard | None:
    """Conversation-first orchestrator — Phase 2b.

    Delegates to the `_from_context` variants of classification, detection,
    and gap question generation. Deterministic routing (step 3) and assembly
    (step 5) are unchanged — they don't depend on the input shape.
    """
    try:
        question_type = run_question_classification_from_context(boundary, context)
    except Exception:
        _LOGGER.exception("Question classification (from_context) failed")
        return None

    try:
        dimensions = run_dimension_detection_from_context(
            boundary, context, question_type, structural_coverage_routing,
        )
    except Exception:
        _LOGGER.exception("Dimension detection (from_context) failed")
        return None

    gap_routes = route_gap_dimensions(
        dimensions, structural_coverage_routing, anti_echo_model_ids,
    )

    gap_questions: tuple[GapQuestion, ...] = ()
    try:
        gap_questions = generate_gap_questions_from_context(
            boundary, context, question_type, gap_routes, structural_coverage_routing,
        )
    except Exception:
        _LOGGER.exception("Gap question generation (from_context) failed")

    return assemble_structural_coverage_card(
        question_type, dimensions, gap_routes, anti_echo_model_ids, gap_questions,
    )


# ---------------------------------------------------------------------------
# Phase 4b: packet-driven entry points
# ---------------------------------------------------------------------------
# The packet variants produce byte-identical prompts to the context variants
# on inputs where the IR projection is lossless. Known drift: when a
# constraint's status != "active", the packet path emits "[STATUS]" while
# the context path emits "[STATUS/WEIGHT]" because the IR does not carry
# the `weight` field by Phase 1 design.


def _format_classification_from_packet_user_prompt(packet: Lane4Packet) -> str:
    """Packet-driven counterpart to `_format_classification_from_context_user_prompt`."""
    parts: list[str] = ["CONTEXT (scaffolding — classify the user's actual question, not this summary):"]
    if packet.decision_situation:
        parts.append(f"- Decision situation: {packet.decision_situation.text}")
    if packet.original_framing:
        parts.append(f"- Framing extracted upstream: {packet.original_framing.text}")

    assistant_turns = [t for t in packet.turns if t.speaker == "assistant"]
    if assistant_turns:
        parts.append("- Assistant replies (context for what the user was engaging with):")
        for t in assistant_turns:
            parts.append(f"  [Turn {t.turn_index} ASSISTANT] {t.text[:500]}")

    parts.append("")
    parts.append("SOURCE (the user's actual turns — first user turn is the canonical question anchor):")
    for t in packet.turns:
        if t.speaker == "user":
            parts.append(f"[Turn {t.turn_index}] USER:")
            parts.append(t.text)
            parts.append("")

    return "\n".join(parts)


def run_question_classification_from_packet(
    boundary: _BoundaryClient,
    packet: Lane4Packet,
) -> str:
    """Packet-driven question classification."""
    user_prompt = _format_classification_from_packet_user_prompt(packet)
    raw = boundary.run_json(_QUESTION_CLASSIFICATION_SYSTEM_FROM_CONTEXT, user_prompt)
    qtype = coerce_str(raw.get("question_type", ""))
    if qtype not in _VALID_QUESTION_TYPES:
        _LOGGER.warning("Invalid question_type %r, defaulting to decision-evaluation", qtype)
        qtype = "decision-evaluation"
    return qtype


def _format_dimension_detection_from_packet_user_prompt(
    packet: Lane4Packet,
    question_type: str,
    dimension_catalog_text: str,
) -> str:
    """Packet-driven counterpart to `_format_dimension_detection_from_context_user_prompt`."""
    parts: list[str] = [
        f"QUESTION TYPE: {question_type}",
        "",
        f"DIMENSION CATALOG:",
        dimension_catalog_text,
        "",
        "CONTEXT (scaffolding — not the primary source of truth for detection or coverage):",
    ]
    if packet.decision_situation:
        parts.append(f"- Decision situation: {packet.decision_situation.text}")
    if packet.original_framing:
        parts.append(f"- Framing extracted upstream: {packet.original_framing.text}")
    if packet.constraints:
        parts.append("- Constraints:")
        for c in packet.constraints:
            status = c.status or "active"
            tag = status.upper()  # weight not in IR; only matters for non-active
            parts.append(f"  - [{tag}] {c.text} (turn {c.introduced_at_turn})")
    if packet.issues:
        parts.append("- Dropped threads:")
        for i in packet.issues:
            line = (
                f"  - {i.text} (raised by {i.raised_by} turn {i.introduced_at_turn}, "
                f"status: {i.status or '?'})"
            )
            if i.superseded_by:
                line += f", superseded_by: {i.superseded_by}"
            parts.append(line)

    parts.append("")
    parts.append("SOURCE (primary — USER turns establish the question for detection; ASSISTANT turns establish the answer for coverage):")
    for t in packet.turns:
        parts.append(f"[Turn {t.turn_index}] {t.speaker.upper()}:")
        parts.append(t.text)
        parts.append("")

    return "\n".join(parts)


def run_dimension_detection_from_packet(
    boundary: _BoundaryClient,
    packet: Lane4Packet,
    question_type: str,
    structural_coverage_routing: dict,
) -> tuple[DetectedDimension, ...]:
    """Packet-driven dimension detection."""
    catalog_text = _build_dimension_catalog_text(structural_coverage_routing)
    user_prompt = _format_dimension_detection_from_packet_user_prompt(
        packet, question_type, catalog_text,
    )
    raw = boundary.run_json(_DIMENSION_DETECTION_SYSTEM_FROM_CONTEXT, user_prompt)
    return _parse_dimension_detection(raw)


def _format_gap_question_from_packet_user_prompt(
    packet: Lane4Packet,
    question_type: str,
    gap_routes: tuple[DimensionRoute, ...],
    structural_coverage_routing: dict,
) -> str:
    """Packet-driven counterpart to `_format_gap_question_from_context_user_prompt`."""
    routing_dims = structural_coverage_routing.get("dimensions", {})
    gap_sections: list[str] = []
    for route in gap_routes:
        dim_def = routing_dims.get(route.dimension_id, {})
        gap_sections.append(
            f"GAP DIMENSION: {route.dimension_name} (id: {route.dimension_id})\n"
            f"Cleaving frame: {dim_def.get('cleaving_frame', 'N/A')}\n"
            f"What's missing: The assistant did not address this dimension.\n"
            f"Why it matters: {dim_def.get('materiality_test', 'N/A')}"
        )

    parts: list[str] = [
        f"QUESTION TYPE: {question_type}",
        "",
        "CONTEXT (scaffolding — do NOT quote verbatim into your questions; use only for grounding):",
    ]
    if packet.decision_situation:
        parts.append(f"- Decision situation: {packet.decision_situation.text}")
    if packet.original_framing:
        parts.append(f"- Framing extracted upstream: {packet.original_framing.text}")
    if packet.constraints:
        parts.append("- Constraints:")
        for c in packet.constraints:
            status = c.status or "active"
            tag = status.upper()
            parts.append(f"  - [{tag}] {c.text} (turn {c.introduced_at_turn})")

    parts.append("")
    parts.append("SOURCE (the real conversation — your questions should reference particulars from here):")
    for t in packet.turns:
        parts.append(f"[Turn {t.turn_index}] {t.speaker.upper()}:")
        parts.append(t.text)
        parts.append("")

    parts.append("")
    parts.append("STRUCTURAL GAPS:")
    parts.append("")
    parts.append("\n\n".join(gap_sections))

    return "\n".join(parts)


def generate_gap_questions_from_packet(
    boundary: _BoundaryClient,
    packet: Lane4Packet,
    question_type: str,
    gap_routes: tuple[DimensionRoute, ...],
    structural_coverage_routing: dict,
) -> tuple[GapQuestion, ...]:
    """Packet-driven gap question generation. No-op when no gap routes."""
    if not gap_routes:
        return ()

    user_prompt = _format_gap_question_from_packet_user_prompt(
        packet, question_type, gap_routes, structural_coverage_routing,
    )
    raw = boundary.run_json(_GAP_QUESTION_GENERATION_SYSTEM, user_prompt)
    parsed = _parse_gap_questions(raw)

    results: list[GapQuestion] = []
    for route in gap_routes:
        questions = parsed.get(route.dimension_id)
        if questions:
            results.append(GapQuestion(
                dimension_id=route.dimension_id,
                dimension_name=route.dimension_name,
                questions=questions,
            ))
    return tuple(results)


def run_structural_coverage_from_ir(
    boundary: _BoundaryClient,
    ir: ConversationIR,
    structural_coverage_routing: dict,
    anti_echo_model_ids: set[str],
) -> StructuralCoverageCard | None:
    """IR-driven orchestrator. Mirrors `run_structural_coverage_from_context`
    but builds a Lane4Packet from the IR and delegates to packet-driven
    classification, detection, and gap question generation. Deterministic
    routing + assembly are shared (input-shape agnostic)."""
    packet = build_lane4_packet(ir)

    try:
        question_type = run_question_classification_from_packet(boundary, packet)
    except Exception:
        _LOGGER.exception("Question classification (from_ir) failed")
        return None

    try:
        dimensions = run_dimension_detection_from_packet(
            boundary, packet, question_type, structural_coverage_routing,
        )
    except Exception:
        _LOGGER.exception("Dimension detection (from_ir) failed")
        return None

    gap_routes = route_gap_dimensions(
        dimensions, structural_coverage_routing, anti_echo_model_ids,
    )

    gap_questions: tuple[GapQuestion, ...] = ()
    try:
        gap_questions = generate_gap_questions_from_packet(
            boundary, packet, question_type, gap_routes, structural_coverage_routing,
        )
    except Exception:
        _LOGGER.exception("Gap question generation (from_ir) failed")

    return assemble_structural_coverage_card(
        question_type, dimensions, gap_routes, anti_echo_model_ids, gap_questions,
    )
