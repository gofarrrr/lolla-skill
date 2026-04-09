"""Frame Pressure Lane (Lane 3): frame extraction, routing, and card assembly.

This module implements the experimental Frame Pressure lane, which audits the
*question* for embedded assumptions, mutable constraints, and suppressed
counterfactuals.  Unlike Lane 1 (answer-level tendency detection) and Lane 2
(answer-level model companion), Lane 3 reads the question as a reasoning
artifact worth auditing.

The entire lane is gated on ``PipelineConfig.enable_frame_pressure``.  When the
flag is off, no code in this module executes and the frame card is ``None``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal, Protocol

_LOGGER = logging.getLogger("system_b.frame_pressure")


# ---------------------------------------------------------------------------
# Public dataclasses — payload shape for the Frame Pressure lane
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExtractedFrameElement:
    """A single frame-level observation extracted from the query."""

    element_text: str
    element_type: Literal["assumption", "mutable_constraint", "suppressed_counterfactual"]
    evidence_quote: str  # must be a literal substring of the query
    frame_pattern: str  # from curated taxonomy
    fragility_signal: str  # what would break this element
    inquiry_stage: Literal["why", "what_if", "how"]
    likely_default: Literal["ego", "social", "inertia", "emotion", "none"] = "none"


@dataclass(frozen=True)
class Reframing:
    """A concrete alternative question generated from a frame element."""

    reframed_question: str
    what_opens: str  # what reasoning path becomes available
    reframe_move_type: Literal["inversion", "perspective_shift", "scope_expansion", "constraint_relaxation"]
    grounding_model: str  # model_id that drives the reframe
    source_element_index: int = 0  # index into frame_elements


@dataclass(frozen=True)
class FrameRoute:
    """Deterministic routing result for one extracted frame element."""

    element_index: int
    frame_pattern: str
    candidate_model_ids: tuple[str, ...]  # after anti-echo exclusion
    excluded_model_ids: tuple[str, ...]  # models excluded by anti-echo


@dataclass(frozen=True)
class FramePressureCard:
    """The output artifact of the Frame Pressure lane."""

    frame_elements: tuple[ExtractedFrameElement, ...] = ()
    reframings: tuple[Reframing, ...] = ()  # max 2
    anti_echo_model_ids: tuple[str, ...] = ()  # models excluded (Lane 1 overlap)
    overlap_flags: tuple[str, ...] = ()  # frame patterns that overlap Lane 1 at pressure-concept level

    def to_payload(self) -> dict:
        """Serialize to JSON-compatible dict for Observatory / eval surfaces."""
        return {
            "frame_elements": [
                {
                    "element_text": el.element_text,
                    "element_type": el.element_type,
                    "evidence_quote": el.evidence_quote,
                    "frame_pattern": el.frame_pattern,
                    "fragility_signal": el.fragility_signal,
                    "inquiry_stage": el.inquiry_stage,
                    "likely_default": el.likely_default,
                }
                for el in self.frame_elements
            ],
            "reframings": [
                {
                    "reframed_question": r.reframed_question,
                    "what_opens": r.what_opens,
                    "reframe_move_type": r.reframe_move_type,
                    "grounding_model": r.grounding_model,
                    "source_element_index": r.source_element_index,
                }
                for r in self.reframings
            ],
            "anti_echo_model_ids": list(self.anti_echo_model_ids),
            "overlap_flags": list(self.overlap_flags),
        }

    @classmethod
    def from_payload(cls, data: dict) -> "FramePressureCard":
        """Deserialize from a JSON-compatible dict."""
        elements = tuple(
            ExtractedFrameElement(
                element_text=el.get("element_text", ""),
                element_type=el.get("element_type", "assumption"),
                evidence_quote=el.get("evidence_quote", ""),
                frame_pattern=el.get("frame_pattern", ""),
                fragility_signal=el.get("fragility_signal", ""),
                inquiry_stage=el.get("inquiry_stage", "how"),
                likely_default=el.get("likely_default", "none"),
            )
            for el in data.get("frame_elements", [])
        )
        reframings = tuple(
            Reframing(
                reframed_question=r.get("reframed_question", ""),
                what_opens=r.get("what_opens", ""),
                reframe_move_type=r.get("reframe_move_type", "scope_expansion"),
                grounding_model=r.get("grounding_model", ""),
                source_element_index=int(r.get("source_element_index", 0)),
            )
            for r in data.get("reframings", [])
        )
        return cls(
            frame_elements=elements,
            reframings=reframings,
            anti_echo_model_ids=tuple(data.get("anti_echo_model_ids", [])),
            overlap_flags=tuple(data.get("overlap_flags", [])),
        )


# ---------------------------------------------------------------------------
# Boundary protocol (same shape as pipeline.BoundaryClient)
# ---------------------------------------------------------------------------

class _BoundaryClient(Protocol):
    def run_json(self, system_prompt: str, user_prompt: str) -> dict: ...


# ---------------------------------------------------------------------------
# Frame extraction prompt and parser
# ---------------------------------------------------------------------------

_FRAME_EXTRACTION_SYSTEM = """\
You are a frame analyst. Your job is to read a QUESTION and identify embedded \
frame-level assumptions, mutable constraints, and suppressed counterfactuals \
that shape the answer space before any reasoning begins.

You are NOT analyzing the answer. You are analyzing the QUESTION ITSELF as a \
reasoning artifact.

Return a JSON object with a single key "frame_elements" containing a list of \
0-5 extracted elements. Each element has:
  - element_text: what the question assumes, constrains, or suppresses
  - element_type: "assumption" | "mutable_constraint" | "suppressed_counterfactual"
  - evidence_quote: a LITERAL SUBSTRING of the query that grounds this element
  - frame_pattern: the pattern from this taxonomy: binary_collapse, \
borrowed_premise, scope_lock, temporal_fixation, proxy_optimization, \
option_space_collapse, single_actor_assumption, commitment_escalation, \
symptom_as_problem, counterfactual_suppression, habitual_frame, \
premature_intellectualization, means_end_conflation, externalized_agency, \
survivorship_frame
  - fragility_signal: what fact or reframe would break this element
  - inquiry_stage: "why" | "what_if" | "how" (where is the question stuck?)
  - likely_default: "ego" | "social" | "inertia" | "emotion" | "none"

CALIBRATION RULES:
- A frame element is worth surfacing ONLY if dropping it would change the SET \
OF ACCEPTABLE ANSWERS, not just the emphasis within the current answer.
- SILENCE IS A VALID AND OFTEN CORRECT RESULT. If the question is already \
well-formed, exploratory in the right way, or operational with a bounded \
solution space, return {"frame_elements": []}.
- OVERTHINKING GATE: Do NOT surface elements for routine operational/execution \
queries where the solution space is known. Frame pressure is for decisions with \
genuine ambiguity about what the right question is.
- FELT DIFFICULTY TEST: If the query is already a genuine exploration, the \
asker is in the right cognitive state. Focus on pre-packaged formulations.
- If you are unsure whether an observation is a real frame error or merely \
normal problem setup, choose SILENCE.
- Do NOT extract frame elements from direct how-to, debugging, troubleshooting, \
configuration, implementation, drafting, or prioritization requests when the \
user is already asking for a systematic approach inside a known problem space.
- TECHNICAL CONSTRAINT RULE: When a query names a specific technology, algorithm, \
tool, or approach (e.g. "token bucket", "Redis", "Kubernetes", "polymorphic \
relationship"), that is a LEGITIMATE TECHNICAL CHOICE, not a frame error. \
Technical constraints chosen by the asker are part of the problem specification. \
Do NOT flag them as scope_lock, option_space_collapse, or borrowed_premise \
unless an external authority imposed the constraint and the asker is unaware \
of alternatives.
- OPERATIONAL EXECUTION RULE: Queries about sprint planning, report drafting, \
CI/CD setup, database migration, performance reviews, cost optimization, rate \
limiting, or similar bounded engineering/management tasks are operational. \
Return silence unless the query contains a genuinely distorted assumption that \
would change the acceptable answer set if removed.
- NEGATIVE EXAMPLES (MUST return {"frame_elements": []}):
  - "How should I configure resource limits for our Kubernetes pods ... ?"
  - "What systematic approach should we take to find the leak?"
  - "Can you help me draft Q3 OKRs for our platform engineering team?"
  - "Should I use a token bucket or sliding window algorithm with Redis?"
  - "How do I add a polymorphic relationship to our PostgreSQL schema?"
  - "What should we prioritize in our technical debt sprint?"
  - "How do I set up a CI/CD pipeline for a Go monorepo with 15 microservices?"
  - "Help me write a performance review for an engineer who exceeded expectations"
  - "Our AWS bill went from $45K to $120K. The CFO wants it under $80K."
  - "How do I structure a board presentation showing mixed quarterly results?"
  - "How do I set up path-based triggers in our CI/CD pipeline?"
- `borrowed_premise` is HIGH BAR ONLY. Use it only when the question explicitly \
inherits a premise from an authority, stakeholder, vendor, competitor, or \
consensus source AND that inherited premise narrows the option space before \
reasoning begins. A manager's goal, a CFO's budget target, or a team's \
technical choice are NOT borrowed premises — they are normal constraints.
- Do NOT use `borrowed_premise` just because the question contains goals, \
constraints, accepted facts, or a normal project brief.
- `scope_lock` requires that the question's boundary EXCLUDES relevant actors \
or systems. A sprint scope, a single team, or a single service is NOT scope \
lock unless there is evidence the real problem extends beyond that boundary.
- `option_space_collapse` requires that VIABLE, QUALITATIVELY DIFFERENT options \
are suppressed. Two standard algorithm choices for a known problem are NOT \
option space collapse — they are the natural solution set.
- Trivially true observations, routine planning constraints, and ordinary \
technical parameters are NOT frame elements.
- evidence_quote MUST be a literal substring of the query text.
- If no frame elements meet the threshold, return {"frame_elements": []}.
"""


def _format_frame_extraction_user_prompt(query: str, vanilla_answer: str) -> str:
    return (
        f"QUERY (primary signal — analyze this):\n{query}\n\n"
        f"VANILLA ANSWER (secondary — shows where the answer inherited the frame):\n{vanilla_answer}"
    )


def _normalize_quotes(text: str) -> str:
    """Normalize escaped JSON quotes for substring matching."""
    return text.replace('\\"', '"').replace("\\'", "'")


def _strip_wrapping_quotes(text: str) -> str:
    """Strip leading/trailing quote characters that LLMs sometimes add."""
    s = text.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in {"'", '"'}:
        s = s[1:-1].strip()
    return s


def _evidence_in_text(evidence: str, text: str) -> bool:
    """Check if evidence appears in text, tolerant of quote escaping and wrapping."""
    if evidence in text:
        return True
    norm_ev = _normalize_quotes(evidence)
    norm_text = _normalize_quotes(text)
    if norm_ev in norm_text:
        return True
    # Try stripping wrapping quotes the LLM may have added
    stripped = _strip_wrapping_quotes(norm_ev)
    if stripped != norm_ev and stripped in norm_text:
        return True
    return False


def _parse_frame_extraction(raw: dict, query: str) -> tuple[ExtractedFrameElement, ...]:
    """Parse frame extraction LLM output into typed dataclasses."""
    elements: list[ExtractedFrameElement] = []
    for item in raw.get("frame_elements", []):
        evidence = item.get("evidence_quote", "")
        # Validate evidence grounding (normalize escaped quotes for matching)
        if evidence and not _evidence_in_text(evidence, query):
            _LOGGER.warning(
                "Frame element evidence_quote not found in query, skipping: %r",
                evidence[:80],
            )
            continue
        try:
            el = ExtractedFrameElement(
                element_text=item.get("element_text", ""),
                element_type=item.get("element_type", "assumption"),
                evidence_quote=evidence,
                frame_pattern=item.get("frame_pattern", ""),
                fragility_signal=item.get("fragility_signal", ""),
                inquiry_stage=item.get("inquiry_stage", "how"),
                likely_default=item.get("likely_default", "none"),
            )
            elements.append(el)
        except (TypeError, ValueError) as exc:
            _LOGGER.warning("Could not parse frame element: %s", exc)
    return tuple(elements)


# ---------------------------------------------------------------------------
# Public entry point — called by pipeline.py
# ---------------------------------------------------------------------------

def run_frame_extraction(
    boundary: _BoundaryClient,
    query: str,
    vanilla_answer: str,
) -> FramePressureCard:
    """Run the frame extraction boundary call and return a FramePressureCard.

    This is the Phase 1 entry point.  It performs extraction only — no routing
    or reframe generation yet (those are Phase 2 and Phase 3).
    """
    user_prompt = _format_frame_extraction_user_prompt(query, vanilla_answer)
    raw = boundary.run_json(_FRAME_EXTRACTION_SYSTEM, user_prompt)
    elements = _parse_frame_extraction(raw, query)
    return FramePressureCard(frame_elements=elements)


# ---------------------------------------------------------------------------
# Phase 2: Deterministic frame-pattern-to-model routing
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Phase 2: Pressure-concept overlap mapping (Level 2 anti-echo)
# ---------------------------------------------------------------------------

# Curated, deterministic mapping from frame patterns to Lane 1 tendency names
# where the same cognitive concept appears at both the question level and the
# answer level.  Per RFC v4: this replaces string overlap between differently-
# grounded texts (query evidence vs answer evidence).
_FRAME_PATTERN_TO_TENDENCY_OVERLAP: dict[str, tuple[str, ...]] = {
    "borrowed_premise": ("authority-misinfluence-tendency",),
    "commitment_escalation": ("inconsistency-avoidance-tendency",),
    "counterfactual_suppression": ("doubt-avoidance-tendency",),
    "proxy_optimization": ("reward-and-punishment-superresponse-tendency",),
    "scope_lock": ("inconsistency-avoidance-tendency",),
    "binary_collapse": ("doubt-avoidance-tendency", "contrast-misreaction-tendency"),
    "temporal_fixation": (),
    "option_space_collapse": ("doubt-avoidance-tendency",),
    "single_actor_assumption": ("excessive-self-regard-tendency",),
    "symptom_as_problem": ("simple-pain-avoiding-psychological-denial",),
    "survivorship_frame": ("availability-misweighing-tendency",),
    "habitual_frame": (),
    "premature_intellectualization": (),
    "means_end_conflation": (),
    "externalized_agency": ("deprival-superreaction-tendency",),
}


def compute_pressure_concept_overlap(
    elements: tuple[ExtractedFrameElement, ...],
    lane1_tendency_ids: set[str],
) -> tuple[str, ...]:
    """Identify frame patterns that overlap with Lane 1 at the pressure-concept level.

    Returns a tuple of frame_pattern names where Lane 1 already covers the same
    cognitive concept at the answer level.  These elements may still be shown
    (question-level vs answer-level is a real distinction) but are flagged as
    overlapping, not presented as novel pressure.
    """
    overlapping: list[str] = []
    for el in elements:
        mapped_tendencies = _FRAME_PATTERN_TO_TENDENCY_OVERLAP.get(el.frame_pattern, ())
        if any(t in lane1_tendency_ids for t in mapped_tendencies):
            overlapping.append(el.frame_pattern)
    return tuple(overlapping)


def route_frame_elements(
    *,
    elements: tuple[ExtractedFrameElement, ...],
    reframing_routing: dict[str, list[str]],
    anti_echo_model_ids: set[str],
) -> tuple[FrameRoute, ...]:
    """Route extracted frame elements to reframing models via compiled KG.

    For each element, looks up its ``frame_pattern`` in the reframing_routing
    table (built by Wave 5 compilation) and returns the candidate models after
    anti-echo exclusion (Level 1: model IDs already in DeltaCard).
    """
    routes: list[FrameRoute] = []
    for idx, el in enumerate(elements):
        all_models = list(reframing_routing.get(el.frame_pattern, []))
        excluded = [m for m in all_models if m in anti_echo_model_ids]
        candidates = [m for m in all_models if m not in anti_echo_model_ids]
        routes.append(FrameRoute(
            element_index=idx,
            frame_pattern=el.frame_pattern,
            candidate_model_ids=tuple(candidates),
            excluded_model_ids=tuple(excluded),
        ))
    return tuple(routes)


# ---------------------------------------------------------------------------
# Phase 3: Reframe generation (LLM boundary call)
# ---------------------------------------------------------------------------

_REFRAME_GENERATION_SYSTEM = """\
You are a reframe generator. Given extracted frame elements from a QUESTION, \
you produce SPECIFIC ALTERNATIVE QUESTIONS that open new reasoning paths.

RULES:
- Each reframing MUST be a concrete question ending in "?".
- Generic advice like "Consider whether X holds" is FAILURE. The reframed \
question must name specific entities, actions, or comparisons from the context.
- GENERATIVE TEST: would a smart person reading what_opens say "that's \
interesting, I want to think about that"? If not, suppress the reframe.
- MINIMAL CHANGE PRINCIPLE: prefer reframings that change ONE element — one \
assumption, one constraint — not wholesale rewrites of the question.
- INVITATION, NOT ACCUSATION: the reframe should feel like opening a door, \
not pointing out a mistake.

For each element, produce a JSON object with:
  - reframed_question: a specific alternative question (must end with "?")
  - what_opens: what reasoning path becomes available (must be specific)
  - reframe_move_type: "inversion" | "perspective_shift" | "scope_expansion" \
| "constraint_relaxation"
  - grounding_model: the model_id that drives this reframe
  - source_element_index: index of the element this reframe addresses

Return {"reframings": [...]}.
"""

_MIN_REFRAME_QUESTION_WORDS = 8
_MIN_WHAT_OPENS_WORDS = 6


def _format_reframe_generation_prompt(
    query: str,
    elements: tuple[ExtractedFrameElement, ...],
    routes: tuple[FrameRoute, ...],
) -> str:
    parts = [f"ORIGINAL QUERY:\n{query}\n"]
    for route in routes:
        if route.element_index >= len(elements):
            continue
        el = elements[route.element_index]
        models = ", ".join(route.candidate_model_ids) if route.candidate_model_ids else "(none)"
        parts.append(
            f"ELEMENT {route.element_index}:\n"
            f"  text: {el.element_text}\n"
            f"  type: {el.element_type}\n"
            f"  evidence: \"{el.evidence_quote}\"\n"
            f"  pattern: {el.frame_pattern}\n"
            f"  fragility: {el.fragility_signal}\n"
            f"  inquiry_stage: {el.inquiry_stage}\n"
            f"  candidate models: {models}\n"
        )
    return "\n".join(parts)


def _is_generic_reframe(reframed_question: str, what_opens: str) -> bool:
    """Return True if the reframe is too generic to be useful."""
    q_words = len(reframed_question.split())
    w_words = len(what_opens.split())
    if q_words < _MIN_REFRAME_QUESTION_WORDS:
        return True
    if w_words < _MIN_WHAT_OPENS_WORDS:
        return True
    # Must be a question
    if "?" not in reframed_question:
        return True
    # Reject known generic patterns
    generic_starters = ("consider whether", "think about", "reflect on")
    lower_q = reframed_question.lower()
    if any(lower_q.startswith(g) for g in generic_starters):
        return True
    return False


def _parse_reframings(raw: dict) -> tuple[Reframing, ...]:
    """Parse reframe generation LLM output, filtering generic results."""
    results: list[Reframing] = []
    for item in raw.get("reframings", []):
        question = str(item.get("reframed_question", "")).strip()
        what_opens = str(item.get("what_opens", "")).strip()
        if _is_generic_reframe(question, what_opens):
            _LOGGER.info("Filtered generic reframe: %r", question[:80])
            continue
        try:
            results.append(Reframing(
                reframed_question=question,
                what_opens=what_opens,
                reframe_move_type=item.get("reframe_move_type", "scope_expansion"),
                grounding_model=str(item.get("grounding_model", "")).strip(),
                source_element_index=int(item.get("source_element_index", 0)),
            ))
        except (TypeError, ValueError) as exc:
            _LOGGER.warning("Could not parse reframing: %s", exc)
    return tuple(results)


def generate_reframings(
    *,
    boundary: _BoundaryClient,
    query: str,
    elements: tuple[ExtractedFrameElement, ...],
    routes: tuple[FrameRoute, ...],
) -> tuple[Reframing, ...]:
    """Run the reframe generation boundary call and return parsed reframings."""
    user_prompt = _format_reframe_generation_prompt(query, elements, routes)
    raw = boundary.run_json(_REFRAME_GENERATION_SYSTEM, user_prompt)
    return _parse_reframings(raw)


# ---------------------------------------------------------------------------
# Phase 3: Card assembly — budget, ranking, provenance
# ---------------------------------------------------------------------------

_MAX_REFRAMINGS = 2


def assemble_frame_card(
    *,
    elements: tuple[ExtractedFrameElement, ...],
    routes: tuple[FrameRoute, ...],
    candidate_reframings: tuple[Reframing, ...],
    anti_echo_model_ids: set[str],
    overlap_flags: tuple[str, ...],
) -> FramePressureCard:
    """Select up to MAX_REFRAMINGS from candidates, preferring move-type diversity.

    Ranking: prefer reframings from diverse move types.  When two reframings have
    the same move type, keep the one that appears earlier (assumed pre-ranked by
    fragility strength + model grounding quality from the caller).
    """
    selected = _select_diverse_reframings(candidate_reframings, _MAX_REFRAMINGS)
    return FramePressureCard(
        frame_elements=elements,
        reframings=tuple(selected),
        anti_echo_model_ids=tuple(sorted(anti_echo_model_ids)),
        overlap_flags=overlap_flags,
    )


def _select_diverse_reframings(
    candidates: tuple[Reframing, ...],
    budget: int,
) -> list[Reframing]:
    """Pick up to *budget* reframings, maximising move-type diversity."""
    if len(candidates) <= budget:
        return list(candidates)
    # First pass: one per move type (in order — earlier = higher ranked)
    selected: list[Reframing] = []
    seen_types: set[str] = set()
    for r in candidates:
        if r.reframe_move_type not in seen_types:
            selected.append(r)
            seen_types.add(r.reframe_move_type)
            if len(selected) == budget:
                return selected
    # Second pass: fill remaining slots in rank order
    for r in candidates:
        if r not in selected:
            selected.append(r)
            if len(selected) == budget:
                return selected
    return selected
