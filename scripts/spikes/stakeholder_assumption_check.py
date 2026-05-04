#!/usr/bin/env python3
"""Offline stakeholder-assumption check harness.

This module is intentionally experimental and fixture-first. It does not run
live LLM calls and is not wired into `/lolla` runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


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
    """Decide whether the offline checker should run.

    The trigger is conservative: named actors alone are not enough. We need a
    material structural dimension or a plan dependency tied to an actor.
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

    if actors and material_gaps and has_dependency:
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


if __name__ == "__main__":
    raise SystemExit(main())
