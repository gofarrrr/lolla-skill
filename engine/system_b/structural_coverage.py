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

_QUESTION_CLASSIFICATION_SYSTEM = """\
You are a question classifier. Your job is to classify a question into exactly \
one of four structural types based on what kind of answer the question demands.

The four types:
  - "causal-diagnosis" — The question asks WHY something happened or is happening. \
It demands root-cause reasoning. Examples: "Why are sales down?", \
"What's causing the high churn rate?"
  - "decision-evaluation" — The question asks WHETHER to do something. \
It demands trade-off and commitment reasoning. Examples: "Should we sign \
the deal?", "Is it worth expanding into Europe?"
  - "action-planning" — The question asks HOW to do something. \
It demands sequencing and execution reasoning. The decision is already made; \
the question is about implementation. Examples: "How do we restructure \
the engineering org?", "What's the plan for the product launch?"
  - "prediction" — The question asks WHAT WILL HAPPEN. It demands forecasting \
and scenario reasoning. Examples: "What happens if we raise prices 20%?", \
"Where will the market be in 3 years?"

Return a JSON object: {"question_type": "<type>"}

Rules:
- Pick the DOMINANT type. Many questions blend types — choose the one that \
best captures what kind of reasoning the answer needs.
- If the question is ambiguous, default to "decision-evaluation" — most \
strategic questions are fundamentally about whether to act.
- Return ONLY the JSON object. No explanation.
"""


def _format_classification_user_prompt(query: str, vanilla_answer: str) -> str:
    return (
        f"QUESTION:\n{query}\n\n"
        f"ANSWER (for context only — classify the QUESTION, not the answer):\n"
        f"{vanilla_answer[:1000]}"
    )


_VALID_QUESTION_TYPES = frozenset({
    "causal-diagnosis",
    "decision-evaluation",
    "action-planning",
    "prediction",
})


def run_question_classification(
    boundary: _BoundaryClient,
    query: str,
    vanilla_answer: str,
) -> str:
    """Classify the question into one of 4 structural types."""
    user_prompt = _format_classification_user_prompt(query, vanilla_answer)
    raw = boundary.run_json(_QUESTION_CLASSIFICATION_SYSTEM, user_prompt)
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


_DIMENSION_DETECTION_SYSTEM = """\
You are a structural coverage analyst. Your job is to examine a QUESTION and \
its ANSWER and determine which structural dimensions of the problem are present \
and whether the answer addresses each one.

You will receive:
1. The question type (causal-diagnosis, decision-evaluation, action-planning, prediction)
2. A catalog of 15 structural dimensions with detect_when conditions and coverage signals
3. The question and vanilla answer

Your task:
1. DETECT: Which dimensions are structurally present in this problem? Use the \
detect_when conditions. A dimension is present if at least 2 of its detect_when \
conditions are clearly met. Only consider dimensions whose question_types include \
the classified question type.
2. ASSESS COVERAGE: For each detected dimension, does the answer engage with \
the structural tension described by the dimension's cleaving frame? \
Use the coverage signals as a guide, but apply this test: the answer must \
directly reason about the dimension's core trade-off — not merely mention \
a related topic in passing. A dimension is "covered" ONLY if the answer \
explicitly engages with the structural tension and reaches a position on it.
3. MATERIALITY GATE: For each uncovered dimension, apply the materiality test. \
Only flag it as a gap if addressing it would plausibly change the decision or action.

Return a JSON object:
{
  "dimensions": [
    {
      "dimension_id": "<id from catalog>",
      "dimension_name": "<name from catalog>",
      "covered": true/false,
      "coverage_evidence": "<what in the answer addresses this, OR what's missing>",
      "materiality_note": "<why this gap matters for the decision, or 'covered' if addressed>"
    }
  ]
}

Rules:
- Return ONLY dimensions that are structurally present. Do not list dimensions \
that don't apply to this problem.
- Typically 4-8 dimensions fire for a strategic question. Fewer than 3 suggests \
you're being too conservative. More than 10 suggests you're not applying the \
detect_when conditions strictly enough.
- The materiality gate is crucial. A dimension is a gap ONLY if addressing it \
would change the recommendation. If the dimension is present but immaterial \
(addressing it wouldn't change anything), mark it as covered with \
coverage_evidence explaining why it's immaterial.
- Be specific in coverage_evidence. Quote or paraphrase the answer where it \
addresses a dimension. For gaps, explain what's structurally missing.
- CRITICAL — Mentioning is not covering. Apply these tests before marking covered:
  * Stakeholder Alignment: Discussing people involved in a deal is NOT \
stakeholder analysis. Covered requires: who must APPROVE, who can BLOCK, \
and what the influence strategy is for getting agreement.
  * Timing & Sequencing: Listing timeframes in a deal structure is NOT \
sequencing analysis. Covered requires: why this order rather than another, \
what the critical path is, or whether delay helps or hurts.
  * Commitment & Reversibility: Proposing staged deal terms is NOT \
reversibility analysis. Covered requires: what happens if you want to \
EXIT or UNWIND, what lock-in costs exist, what optionality is consumed.
  * Uncertainty Type: Presenting scenarios with specific numbers is NOT \
uncertainty classification. Covered requires: distinguishing what is \
knowable from what is genuinely uncertain, and matching the approach to \
the uncertainty type.
  * Information Quality: Adjusting numbers for known risks is NOT \
evidence quality analysis. Covered requires: questioning the reliability \
of the data sources, identifying what evidence is missing, or checking \
whether claims rest on biased or unrepresentative samples.
- Return ONLY the JSON object. No explanation.
"""


def _format_dimension_detection_user_prompt(
    query: str,
    vanilla_answer: str,
    question_type: str,
    dimension_catalog_text: str,
) -> str:
    return (
        f"QUESTION TYPE: {question_type}\n\n"
        f"DIMENSION CATALOG:\n{dimension_catalog_text}\n\n"
        f"QUESTION:\n{query}\n\n"
        f"VANILLA ANSWER:\n{vanilla_answer}"
    )


def run_dimension_detection(
    boundary: _BoundaryClient,
    query: str,
    vanilla_answer: str,
    question_type: str,
    structural_coverage_routing: dict,
) -> tuple[DetectedDimension, ...]:
    """Detect structural dimensions and assess coverage."""
    catalog_text = _build_dimension_catalog_text(structural_coverage_routing)
    user_prompt = _format_dimension_detection_user_prompt(
        query, vanilla_answer, question_type, catalog_text,
    )
    raw = boundary.run_json(_DIMENSION_DETECTION_SYSTEM, user_prompt)
    return _parse_dimension_detection(raw)


def _parse_dimension_detection(raw: dict) -> tuple[DetectedDimension, ...]:
    """Parse the LLM response into DetectedDimension objects."""
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


def _format_gap_question_user_prompt(
    query: str,
    vanilla_answer: str,
    question_type: str,
    gap_routes: tuple[DimensionRoute, ...],
    structural_coverage_routing: dict,
) -> str:
    """Build the user prompt for gap question generation."""
    routing_dims = structural_coverage_routing.get("dimensions", {})
    gap_sections: list[str] = []
    for route in gap_routes:
        dim_def = routing_dims.get(route.dimension_id, {})
        gap_sections.append(
            f"GAP DIMENSION: {route.dimension_name} (id: {route.dimension_id})\n"
            f"Cleaving frame: {dim_def.get('cleaving_frame', 'N/A')}\n"
            f"What's missing: The answer does not address this dimension.\n"
            f"Why it matters: {dim_def.get('materiality_test', 'N/A')}"
        )
    return (
        f"QUESTION TYPE: {question_type}\n\n"
        f"QUESTION:\n{query}\n\n"
        f"VANILLA ANSWER (first 1500 chars):\n{vanilla_answer[:1500]}\n\n"
        f"STRUCTURAL GAPS:\n\n" + "\n\n".join(gap_sections)
    )


def generate_gap_questions(
    boundary: _BoundaryClient,
    query: str,
    vanilla_answer: str,
    question_type: str,
    gap_routes: tuple[DimensionRoute, ...],
    structural_coverage_routing: dict,
) -> tuple[GapQuestion, ...]:
    """Generate discovery questions for each gap dimension.

    Returns an empty tuple if there are no gaps (no LLM call made).
    """
    if not gap_routes:
        return ()

    user_prompt = _format_gap_question_user_prompt(
        query, vanilla_answer, question_type, gap_routes, structural_coverage_routing,
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

def run_structural_coverage(
    boundary: _BoundaryClient,
    query: str,
    vanilla_answer: str,
    structural_coverage_routing: dict,
    anti_echo_model_ids: set[str],
) -> StructuralCoverageCard | None:
    """Run the full Structural Coverage lane.

    1. Classify the question type
    2. Detect dimensions and assess coverage
    3. Route uncovered dimensions to models (deterministic, with anti-echo)
    4. Generate gap questions (LLM call, only when gaps exist)
    5. Assemble the coverage card

    Returns ``None`` on hard failure (boundary errors). Returns a card with
    empty dimensions if no dimensions fire (a valid result).
    """
    try:
        # Step 1: Question classification
        question_type = run_question_classification(boundary, query, vanilla_answer)
    except Exception:
        _LOGGER.exception("Question classification failed")
        return None

    try:
        # Step 2: Dimension detection + coverage check
        dimensions = run_dimension_detection(
            boundary, query, vanilla_answer,
            question_type, structural_coverage_routing,
        )
    except Exception:
        _LOGGER.exception("Dimension detection failed")
        return None

    # Step 3: Deterministic routing (no LLM call)
    gap_routes = route_gap_dimensions(
        dimensions, structural_coverage_routing, anti_echo_model_ids,
    )

    # Step 4: Gap question generation (LLM call 3, only when gaps exist)
    gap_questions: tuple[GapQuestion, ...] = ()
    try:
        gap_questions = generate_gap_questions(
            boundary, query, vanilla_answer,
            question_type, gap_routes, structural_coverage_routing,
        )
    except Exception:
        _LOGGER.exception("Gap question generation failed")

    # Step 5: Assembly
    return assemble_structural_coverage_card(
        question_type, dimensions, gap_routes, anti_echo_model_ids, gap_questions,
    )
