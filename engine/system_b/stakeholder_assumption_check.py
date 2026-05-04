"""Stakeholder-assumption check.

Flag-gated support module for a narrow stakeholder lens. It does not try to
model every actor's inner life; it audits when advice depends on another
actor's knowledge, power, cooperation, interpretation, or likely action.
"""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Protocol


MATERIAL_DIMENSIONS = {
    "stakeholder-alignment",
    "incentive-alignment",
    "competitive-dynamics",
    "information-quality",
    "risk-response",
}

COMMUNICATION_TERMS = {
    "ask",
    "tell",
    "share",
    "call",
    "meet",
    "message",
    "email",
    "persuade",
    "convince",
    "notify",
    "disclose",
    "report",
    "approve",
    "approval",
    "align",
    "back",
    "buy-in",
    "buy in",
    "co-advise",
    "co-advising",
    "commit",
    "consent",
    "endorse",
    "fund",
    "green-light",
    "green light",
    "greenlit",
    "handoff",
    "negotiate",
    "sponsor",
    "cooperate",
    "outreach",
    "sign-off",
    "sign off",
    "support",
    "block",
    "retaliate",
    "exit",
}

ROLE_CLOSENESS_TERMS = {
    "closeness",
    "close to",
    "family relationship",
    "likely access",
    "likely-access",
    "role closeness",
    "role/closeness",
}

SPOUSE_ACTOR_TERMS = {"wife", "spouse", "husband", "partner"}
DISCUSSION_ACTION_TERMS = {
    "ask",
    "asked",
    "conversation",
    "discuss",
    "discussed",
    "share",
    "shared",
    "talk",
    "tell",
    "told",
}

GROUNDING_DOWNGRADE_NOTE = "role/closeness inference downgraded from grounded"
PREDICTIVE_DOWNGRADE_NOTE = "behavior prediction downgraded from grounded"

PREDICTIVE_ASSUMPTION_TERMS = {
    " likely ",
    " will ",
    " without pushback",
    " would ",
    " accept ",
    " cooperate",
    " re-open",
    " support ",
    " thaw",
}

PLAN_CHANGE_FIELDS = {
    "plan_change",
    "next_move",
    "recommended_change",
    "suggested_revision",
    "intervention_hint",
    "reframed_question",
    "alternative_question",
    "question",
}

PLAN_STOPWORDS = {
    "a",
    "about",
    "after",
    "all",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "by",
    "can",
    "could",
    "do",
    "does",
    "for",
    "from",
    "have",
    "her",
    "him",
    "how",
    "if",
    "in",
    "is",
    "it",
    "not",
    "of",
    "on",
    "or",
    "she",
    "should",
    "that",
    "the",
    "their",
    "them",
    "then",
    "this",
    "to",
    "what",
    "when",
    "whether",
    "will",
    "with",
    "you",
    "your",
}

ACTOR_ALIASES = {
    "ex": {"ex", "ex-husband", "co-parent", "dad", "father"},
    "wife": {"wife", "spouse"},
    "advisor": {"advisor", "pi", "supervisor"},
    "silva": {"silva", "dr. silva"},
    "marcus": {"marcus"},
    "lina": {"lina"},
    "jake": {"jake"},
    "gc": {"gc", "general counsel"},
}


class JsonBoundary(Protocol):
    def run_json(self, system_prompt: str, user_prompt: str, **kwargs) -> dict:
        ...


SYSTEM_PROMPT = """\
You are Lolla's stakeholder-assumption checker.

Your job is narrow: catch when the advice depends on another actor's
knowledge, interpretation, cooperation, power, silence, retaliation, or exit.

Do NOT write a psychology profile. Do NOT list emotions by default. Do NOT
predict reactions unless the predicted reaction changes a concrete plan.

Return ONLY strict JSON:
{
  "status": "completed",
  "surface": true | false,
  "summary": "one sentence, empty if no material plan change",
  "critical_actors": [
    {
      "actor_id": "short_id",
      "display_name": "human label",
      "role": "role in the decision",
      "power_or_dependency": ["concrete dependency"],
      "advice_assumption": "what the advice assumes about this actor",
      "grounding": "grounded | plausible | speculative",
      "grounding_source": "transcript_fact | role_closeness | inference",
      "known_to_actor": ["only transcript-grounded or clearly plausible facts"],
      "unknown_to_actor": ["facts the advice/user/model has but actor may not"],
      "bridging_facts": ["why actor knows/can affect this, if established"],
      "unsafe_inferences": ["claims the advice must not rely on"],
      "risk_if_wrong": "what breaks if the assumption is false",
      "plan_change": "smallest concrete action/sequence/threshold/content change",
      "open_question": "question the user would need to answer"
    }
  ]
}

Rules:
- If a role/closeness inference is used, mark it plausible, never grounded.
- Speculative assumptions may be listed but must not require surface=true.
- If there is no concrete plan_change, set surface=false.
- Keep at most two critical actors.
"""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def load_annotation(path: Path) -> dict[str, Any]:
    return load_json(path)


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _lower_blob(*parts: Any) -> str:
    return "\n".join(_as_text(p) for p in parts).lower()


def _extract_uncovered_dimensions(result: dict[str, Any]) -> list[dict[str, Any]]:
    card = result.get("structural_coverage_card") or {}
    dimensions = card.get("dimensions") or []
    return [d for d in dimensions if d and d.get("covered") is False]


def _candidate_actors(text: str) -> list[str]:
    found: list[str] = []
    lowered = text.lower()
    for canonical, aliases in ACTOR_ALIASES.items():
        if any(
            re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", lowered)
            for alias in aliases
        ):
            found.append(canonical)
    return found


def _has_plan_dependency(text: str) -> bool:
    padded = f" {text.lower()} "
    return any(f" {term} " in padded or term in padded for term in COMMUNICATION_TERMS)


def evaluate_trigger(
    *,
    extraction: dict[str, Any],
    result: dict[str, Any],
    conversation_text: str = "",
) -> dict[str, Any]:
    """Decide whether the checker should run.

    The trigger is conservative: named actors alone are not enough. We need a
    material structural dimension and a plan dependency tied to an actor.
    """

    blob = _lower_blob(extraction, result, conversation_text)
    actors = _candidate_actors(blob)
    uncovered = _extract_uncovered_dimensions(result)
    material_gaps = [
        d for d in uncovered if str(d.get("dimension_id", "")) in MATERIAL_DIMENSIONS
    ]

    dependency_text = _lower_blob(
        extraction.get("synthesized_position"),
        extraction.get("live_constraints"),
        extraction.get("dropped_threads"),
        [d.get("gap_questions") for d in material_gaps],
    )
    has_dependency = _has_plan_dependency(dependency_text)

    if material_gaps and has_dependency:
        if not actors:
            actors = ["actor_from_structural_gap"]
        dimensions = sorted({str(d.get("dimension_id")) for d in material_gaps})
        return {
            "triggered": True,
            "trigger_reason": "material stakeholder dependency via " + ", ".join(dimensions),
            "skip_reason": "",
            "candidate_actors": actors,
        }

    return {
        "triggered": False,
        "trigger_reason": "",
        "skip_reason": "no material stakeholder dependency detected",
        "candidate_actors": [],
    }


def _has_behavior_prediction(text: Any) -> bool:
    assumption_blob = f" {_lower_blob(text)} "
    return any(term in assumption_blob for term in PREDICTIVE_ASSUMPTION_TERMS)


def _has_role_closeness_inference(actor: dict[str, Any]) -> bool:
    grounding_blob = _lower_blob(
        actor.get("grounding_source"),
        actor.get("bridging_facts"),
        actor.get("unsafe_inferences"),
    )
    return any(term in grounding_blob for term in ROLE_CLOSENESS_TERMS)


def _is_role_closeness_open_question(actor: dict[str, Any]) -> bool:
    if not _has_role_closeness_inference(actor):
        return False
    actor_blob = _lower_blob(
        actor.get("actor_id"),
        actor.get("display_name"),
        actor.get("role"),
    )
    if not any(term in actor_blob for term in SPOUSE_ACTOR_TERMS):
        return False
    return bool(actor.get("unsafe_inferences")) or _has_behavior_prediction(
        actor.get("advice_assumption")
    )


def _is_spouse_actor(actor: dict[str, Any]) -> bool:
    actor_blob = _lower_blob(
        actor.get("actor_id"),
        actor.get("display_name"),
        actor.get("role"),
    )
    return any(term in actor_blob for term in SPOUSE_ACTOR_TERMS)


def _has_discussion_action(text: str) -> bool:
    tokens = set(_plan_tokens(text))
    return bool(tokens & DISCUSSION_ACTION_TERMS)


def _mentions_spouse(text: str) -> bool:
    normalized = f" {_normalized_plan_text(text)} "
    return any(f" {term} " in normalized for term in SPOUSE_ACTOR_TERMS)


def _is_spouse_discussion_duplicate(
    actor: dict[str, Any],
    plan_change: str,
    existing_plan_texts: list[str],
) -> bool:
    if not _is_spouse_actor(actor) or not _has_discussion_action(plan_change):
        return False
    return any(
        _mentions_spouse(existing) and _has_discussion_action(existing)
        for existing in existing_plan_texts
    )


def _normalize_actor(actor: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(actor)
    role_closeness_inference = _has_role_closeness_inference(normalized)
    lacks_known_evidence = not normalized.get("known_to_actor")
    behavior_prediction = _has_behavior_prediction(normalized.get("advice_assumption"))
    if normalized.get("grounding") == "grounded" and (
        role_closeness_inference or lacks_known_evidence or behavior_prediction
    ):
        normalized["grounding"] = "plausible"
        normalized["grounding_note"] = (
            GROUNDING_DOWNGRADE_NOTE
            if role_closeness_inference or lacks_known_evidence
            else PREDICTIVE_DOWNGRADE_NOTE
        )
    return normalized


def _normalized_plan_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(text or "").lower()))


def _root_token(token: str) -> str:
    if len(token) > 6 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 5 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 4 and token.endswith("s"):
        return token[:-1]
    return token


def _plan_tokens(text: str) -> list[str]:
    return [
        _root_token(token)
        for token in re.findall(r"[a-z0-9]+", str(text or "").lower())
        if token not in PLAN_STOPWORDS and len(token) > 2
    ]


def _tokens_match(left: str, right: str) -> bool:
    return left == right or left.startswith(right[:6]) or right.startswith(left[:6])


def _has_high_token_overlap(candidate: str, existing: str) -> bool:
    candidate_tokens = _plan_tokens(candidate)
    existing_tokens = _plan_tokens(existing)
    if min(len(candidate_tokens), len(existing_tokens)) < 4:
        return False
    shared = {
        token
        for token in candidate_tokens
        if any(_tokens_match(token, other) for other in existing_tokens)
    }
    overlap = len(shared) / min(len(candidate_tokens), len(existing_tokens))
    return len(shared) >= 3 and overlap >= 0.6


def _is_duplicate_plan_change(plan_change: str, existing_plan_texts: list[str]) -> bool:
    candidate = _normalized_plan_text(plan_change)
    if not candidate:
        return False
    for existing in existing_plan_texts:
        normalized = _normalized_plan_text(existing)
        if not normalized:
            continue
        if candidate in normalized or normalized in candidate:
            return True
        if _has_high_token_overlap(plan_change, existing):
            return True
    return False


def _collect_existing_plan_texts(
    result: dict[str, Any],
    extraction: dict[str, Any] | None = None,
) -> list[str]:
    texts: list[str] = []

    def collect_text(value: Any) -> None:
        if isinstance(value, str) and value.strip():
            texts.append(value)

    def collect_from_items(items: Any) -> None:
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            for field in PLAN_CHANGE_FIELDS:
                value = item.get(field)
                if isinstance(value, str) and value.strip():
                    texts.append(value)

    frame_card = result.get("frame_pressure_card") or {}
    collect_from_items(frame_card.get("reframings"))
    delta_card = result.get("delta_card") or {}
    collect_from_items(delta_card.get("findings"))
    collect_text((extraction or {}).get("synthesized_position"))
    return texts


def gate_surface(
    check: dict[str, Any],
    *,
    existing_plan_texts: list[str] | None = None,
) -> dict[str, Any]:
    """Apply product surface gates to a checker output."""

    gated = deepcopy(check)
    existing_texts = existing_plan_texts or []
    actors = [_normalize_actor(a) for a in gated.get("critical_actors") or []]
    chat_actors: list[dict[str, Any]] = []
    with_plan_change: list[dict[str, Any]] = []
    duplicate_plan_change: list[dict[str, Any]] = []

    for actor in actors:
        plan_change = str(actor.get("plan_change") or "").strip()
        if not plan_change:
            actor["surface_in_chat"] = False
            actor["surface_block_reason"] = "no_concrete_plan_change"
            continue

        with_plan_change.append(actor)
        if actor.get("grounding") == "speculative":
            actor["surface_in_chat"] = False
            actor["surface_block_reason"] = "speculative"
            continue

        if _is_role_closeness_open_question(actor):
            actor["surface_in_chat"] = False
            actor["surface_block_reason"] = "role_closeness_open_question"
            continue

        if _is_spouse_discussion_duplicate(
            actor,
            plan_change,
            existing_texts,
        ) or _is_duplicate_plan_change(plan_change, existing_texts):
            actor["surface_in_chat"] = False
            actor["surface_block_reason"] = "duplicate_existing_advice"
            duplicate_plan_change.append(actor)
            continue

        actor["surface_in_chat"] = True
        actor["surface_block_reason"] = ""
        chat_actors.append(actor)

    gated["critical_actors"] = actors
    gated["chat_actors"] = chat_actors

    if not with_plan_change:
        gated["surface"] = False
        gated["surface_reason"] = "no surfaced actor has a concrete plan_change"
        return gated

    if not chat_actors:
        gated["surface"] = False
        if all(a.get("grounding") == "speculative" for a in with_plan_change):
            gated["surface_reason"] = "all surfaced assumptions are speculative"
        elif duplicate_plan_change and len(duplicate_plan_change) == len(with_plan_change):
            gated["surface_reason"] = "all plan-changing actors duplicate existing advice"
        else:
            gated["surface_reason"] = "no actor passed chat surface gates"
        return gated

    gated["surface"] = bool(gated.get("surface", True))
    gated["surface_reason"] = (
        "plan-changing grounded-or-plausible assumption"
        if gated["surface"]
        else "checker returned surface=false after actor-level gating"
    )
    return gated


def _compact_result_for_prompt(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "delta_card": result.get("delta_card") or {},
        "companion_cheat_sheet": result.get("companion_cheat_sheet") or {},
        "frame_pressure_card": result.get("frame_pressure_card") or {},
        "structural_coverage_card": result.get("structural_coverage_card") or {},
        "revised_answer": result.get("revised_answer") or "",
        "gap_check_summary": result.get("gap_check_summary") or "",
    }


def build_checker_prompt(
    *,
    extraction: dict[str, Any],
    result: dict[str, Any],
    trigger: dict[str, Any],
    conversation_text: str = "",
) -> str:
    payload = {
        "trigger": trigger,
        "extraction": extraction,
        "audit_result": _compact_result_for_prompt(result),
        "conversation_excerpt": conversation_text[:12000],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _run_boundary(boundary: JsonBoundary, user_prompt: str) -> dict[str, Any]:
    try:
        payload = boundary.run_json(
            SYSTEM_PROMPT,
            user_prompt,
            stage="stakeholder_assumption_check",
        )
    except TypeError:
        payload = boundary.run_json(SYSTEM_PROMPT, user_prompt)
    return payload if isinstance(payload, dict) else {}


def normalize_checker_payload(
    payload: dict[str, Any],
    *,
    trigger: dict[str, Any],
    result: dict[str, Any] | None = None,
    extraction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = dict(payload or {})
    normalized["status"] = "completed"
    normalized["triggered"] = True
    normalized["trigger_reason"] = trigger.get("trigger_reason", "")
    normalized["candidate_actors"] = list(trigger.get("candidate_actors") or ())
    normalized["critical_actors"] = [
        a for a in (normalized.get("critical_actors") or []) if isinstance(a, dict)
    ][:2]
    normalized.setdefault("summary", "")
    normalized.setdefault("surface", bool(normalized["critical_actors"]))
    return gate_surface(
        normalized,
        existing_plan_texts=_collect_existing_plan_texts(result or {}, extraction),
    )


def run_stakeholder_assumption_check(
    *,
    extraction: dict[str, Any],
    result: dict[str, Any],
    conversation_text: str = "",
    boundary: JsonBoundary | None = None,
) -> tuple[dict[str, Any], list[Any]]:
    """Run the trigger and optional LLM checker.

    Returns ``(payload, call_log)``. ``call_log`` is empty for skipped cases and
    populated from the boundary client when a model call occurs.
    """

    trigger = evaluate_trigger(
        extraction=extraction,
        result=result,
        conversation_text=conversation_text,
    )
    if not trigger.get("triggered"):
        return {
            "status": "skipped",
            "triggered": False,
            "trigger_reason": "",
            "skip_reason": trigger.get("skip_reason", ""),
            "candidate_actors": [],
            "surface": False,
            "critical_actors": [],
            "chat_actors": [],
        }, []

    if boundary is None:
        return {
            "status": "skipped_error",
            "triggered": True,
            "trigger_reason": trigger.get("trigger_reason", ""),
            "skip_reason": "",
            "candidate_actors": list(trigger.get("candidate_actors") or ()),
            "surface": False,
            "critical_actors": [],
            "chat_actors": [],
            "error": "boundary client required for triggered stakeholder check",
        }, []

    try:
        raw_payload = _run_boundary(
            boundary,
            build_checker_prompt(
                extraction=extraction,
                result=result,
                trigger=trigger,
                conversation_text=conversation_text,
            ),
        )
        call_log = list(getattr(boundary, "call_log", ()) or ())
    except Exception as exc:  # pragma: no cover - exercised via integration tests
        return {
            "status": "skipped_error",
            "triggered": True,
            "trigger_reason": trigger.get("trigger_reason", ""),
            "skip_reason": "",
            "candidate_actors": list(trigger.get("candidate_actors") or ()),
            "surface": False,
            "critical_actors": [],
            "chat_actors": [],
            "error": str(exc),
        }, list(getattr(boundary, "call_log", ()) or ())

    if not raw_payload:
        return {
            "status": "skipped_error",
            "triggered": True,
            "trigger_reason": trigger.get("trigger_reason", ""),
            "skip_reason": "",
            "candidate_actors": list(trigger.get("candidate_actors") or ()),
            "surface": False,
            "critical_actors": [],
            "chat_actors": [],
            "error": "boundary returned empty stakeholder check payload",
        }, call_log

    return normalize_checker_payload(
        raw_payload,
        trigger=trigger,
        result=result,
        extraction=extraction,
    ), call_log


def _norm(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def _contains_or_equal(haystack: str, needle: str) -> bool:
    h = _norm(haystack)
    n = _norm(needle)
    return bool(n and (n in h or h in n))


def score_check(
    *,
    annotation: dict[str, Any],
    trigger: dict[str, Any],
    check: dict[str, Any],
) -> dict[str, Any]:
    expected = annotation.get("expected") or {}
    actors = (
        check.get("chat_actors")
        if "chat_actors" in check
        else check.get("critical_actors")
    ) or []
    surfaced = bool(check.get("surface"))
    actor_names = " ".join(
        _as_text(a.get("display_name") or a.get("actor") or a.get("actor_id"))
        for a in actors
    ).lower()

    expected_trigger = bool(expected.get("triggered"))
    trigger_match = bool(trigger.get("triggered")) == expected_trigger
    actor_match = True
    if expected_trigger and expected.get("actor"):
        actor = str(expected["actor"]).lower()
        actor_match = actor in actor_names or actor in (trigger.get("candidate_actors") or [])

    plan_change_match = False
    assumption_match = False
    speculative_surface_violation = False
    for actor in actors:
        if actor.get("grounding") == "speculative" and surfaced:
            speculative_surface_violation = True
        if _contains_or_equal(actor.get("plan_change", ""), expected.get("plan_change", "")):
            plan_change_match = True
        if _contains_or_equal(
            actor.get("advice_assumption", ""),
            expected.get("advice_assumption", ""),
        ):
            assumption_match = True

    return {
        "case_id": annotation.get("case_id"),
        "trigger_match": trigger_match,
        "actor_match": actor_match,
        "assumption_match": assumption_match,
        "plan_change_match": plan_change_match,
        "non_duplicative": bool(expected.get("non_duplicative")) and plan_change_match,
        "speculative_surface_violation": speculative_surface_violation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotation", type=Path)
    parser.add_argument("--extraction", type=Path)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--conversation", type=Path)
    args = parser.parse_args()

    extraction = load_json(args.extraction) if args.extraction else {}
    result = load_json(args.result) if args.result else {}
    conversation = args.conversation.read_text() if args.conversation else ""
    trigger = evaluate_trigger(
        extraction=extraction,
        result=result,
        conversation_text=conversation,
    )

    payload: dict[str, Any] = {"trigger": trigger}
    if args.annotation:
        payload["annotation"] = load_annotation(args.annotation)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0
