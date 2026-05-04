"""Stakeholder-assumption check.

Flag-gated support module for a narrow stakeholder lens. It does not try to
model every actor's inner life; it audits when advice depends on another
actor's knowledge, power, cooperation, interpretation, or likely action.
"""

from __future__ import annotations

import argparse
import json
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
    "sponsor",
    "cooperate",
    "block",
    "retaliate",
    "exit",
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
    padded = f" {text.lower()} "
    for canonical, aliases in ACTOR_ALIASES.items():
        if any(f" {alias} " in padded or alias in padded for alias in aliases):
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


def _normalize_actor(actor: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(actor)
    if (
        normalized.get("grounding") == "grounded"
        and normalized.get("grounding_source") == "role_closeness"
    ):
        normalized["grounding"] = "plausible"
        normalized["grounding_note"] = "role/closeness inference downgraded from grounded"
    return normalized


def gate_surface(check: dict[str, Any]) -> dict[str, Any]:
    """Apply product surface gates to a checker output."""

    gated = deepcopy(check)
    actors = [_normalize_actor(a) for a in gated.get("critical_actors") or []]
    gated["critical_actors"] = actors

    with_plan_change = [
        a for a in actors if str(a.get("plan_change") or "").strip()
    ]
    if not with_plan_change:
        gated["surface"] = False
        gated["surface_reason"] = "no surfaced actor has a concrete plan_change"
        return gated

    non_speculative = [
        a for a in with_plan_change if a.get("grounding") != "speculative"
    ]
    if not non_speculative:
        gated["surface"] = False
        gated["surface_reason"] = "all surfaced assumptions are speculative"
        return gated

    gated["surface"] = bool(gated.get("surface", True))
    gated["surface_reason"] = "plan-changing grounded-or-plausible assumption"
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
    return gate_surface(normalized)


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
            "error": "boundary returned empty stakeholder check payload",
        }, call_log

    return normalize_checker_payload(raw_payload, trigger=trigger), call_log


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
    actors = check.get("critical_actors") or []
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
