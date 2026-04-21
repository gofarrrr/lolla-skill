from __future__ import annotations

from collections import Counter
import json
import re
from typing import Mapping, Sequence

from .companion import CompanionCard
from .companion_selection import CompanionCheatSheet
from .pipeline import BoundaryCallTrace, DeltaCard
from .tendency_catalog import TendencyCatalog


def normalize_text(value: object) -> str:
    return " ".join(str(value or "").split()).strip()


def slugify_case_id(value: object) -> str:
    text = normalize_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "case"


def select_packet_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    only_case_ids: Sequence[str] = (),
    limit: int = 0,
) -> list[dict[str, object]]:
    selected = [dict(row) for row in list(rows or []) if isinstance(row, Mapping)]
    normalized_filters = {slugify_case_id(value) for value in list(only_case_ids or []) if normalize_text(value)}
    if normalized_filters:
        selected = [
            row
            for row in selected
            if slugify_case_id(row.get("case_id", "")) in normalized_filters
        ]
    if int(limit or 0) > 0:
        selected = selected[: int(limit)]
    return selected


def build_case_generation_prompt(case_brief: str) -> str:
    return (
        "You are generating a cheap System B test case.\n"
        "Return ONLY strict JSON with exactly this shape:\n"
        "{\"query\":\"...\",\"vanilla_answer\":\"...\",\"why_this_case\":\"...\"}\n\n"
        "Rules:\n"
        "- `query` must be a realistic user question, request, or decision prompt.\n"
        "- `vanilla_answer` must be a plausible competent answer to that query.\n"
        "- The answer should contain at least one structural weakness or blind spot, but it should still sound useful.\n"
        "- Do not mention System B, testing, prompts, hidden reasoning, or that this is synthetic.\n"
        "- Keep the answer compact enough for repeated packet testing.\n"
        "- Avoid bullet spam unless the brief clearly calls for it.\n\n"
        "CASE BRIEF:\n"
        f"{normalize_text(case_brief)}\n"
    )


def extract_generated_case(payload: Mapping[str, object]) -> dict[str, str]:
    return {
        "query": normalize_text(payload.get("query", "")),
        "vanilla_answer": normalize_text(payload.get("vanilla_answer", "")),
        "why_this_case": normalize_text(payload.get("why_this_case", "")),
    }


def build_revision_prompt(
    *,
    query: str,
    vanilla_answer: str,
    delta_card: DeltaCard,
    companion_card: CompanionCard | None = None,
    companion_cheat_sheet: CompanionCheatSheet | None = None,
) -> str:
    compact_findings = [_finding_payload(finding) for finding in delta_card.findings]
    delta_payload = {
        "detected_tendencies": list(delta_card.detected_tendencies),
        "challenge_statements": list(delta_card.challenge_statements),
        "next_moves": list(delta_card.next_moves),
        "major_tensions": list(delta_card.major_tensions),
        "top_challenge_statements": list(delta_card.top_challenge_statements),
        "secondary_challenge_statements": list(delta_card.secondary_challenge_statements),
        "top_next_moves": list(delta_card.top_next_moves),
        "secondary_next_moves": list(delta_card.secondary_next_moves),
        "top_findings": [_finding_payload(finding) for finding in delta_card.top_findings],
        "secondary_findings": [
            _finding_payload(finding) for finding in delta_card.presented_secondary_findings
        ],
        "secondary_findings_full": [_finding_payload(finding) for finding in delta_card.secondary_findings],
        "secondary_summarization_active": delta_card.secondary_summarization_active,
        "secondary_additional_pressures_note": delta_card.secondary_additional_pressures_note,
        "secondary_additional_pressure_count": delta_card.secondary_additional_pressure_count,
        "secondary_additional_pressure_tendency_ids": list(
            delta_card.secondary_additional_pressure_tendency_ids
        ),
        "compound_groups": [_compound_payload(compound) for compound in delta_card.compound_groups],
        "top_compound_groups": [
            _compound_payload(compound) for compound in delta_card.top_compound_groups
        ],
        "secondary_compound_groups": [
            _compound_payload(compound) for compound in delta_card.secondary_compound_groups
        ],
        "findings": compact_findings,
    }
    # Prefer curated CheatSheet over raw CompanionCard when available.
    # The CheatSheet is budget-bounded, anti-echo filtered, deduplicated,
    # and semantically reranked — a compact version of the raw card.
    if companion_cheat_sheet is not None:
        companion_payload = companion_cheat_sheet.to_payload()
    else:
        companion_payload = companion_card_to_payload(companion_card)
    audit_payload = {
        "delta_card": delta_payload,
        "companion_cheat_sheet": companion_payload,
    }
    return (
        "You are revising an answer after deterministic reasoning pressure from System B.\n"
        "Return ONLY strict JSON with exactly this shape:\n"
        "{\"revised_answer\":\"...\",\"usage_summary\":{\"used_findings\":[],\"used_companion_chunks\":[],\"note\":\"...\"}}\n\n"
        "Rules:\n"
        "- `revised_answer` must stay user-facing and decision-useful.\n"
        "- Preserve what survives from the original answer; do not overwrite it with generic caution.\n"
        "- Treat the delta card as structural challenge pressure: specific weaknesses that should be addressed.\n"
        "- Treat the companion cheat sheet as enrichment from models already active in the answer:\n"
        "  failure modes warn where the answer's own reasoning approach could break;\n"
        "  premortem questions surface what the answer's models would ask before proceeding;\n"
        "  antagonists highlight productive tensions the answer should consider.\n"
        "- Use the pressure to add missing checks, stop-rules, tensions, or failure modes when warranted.\n"
        "- In `used_findings`, list which delta card findings you incorporated.\n"
        "- In `used_companion_chunks`, list which companion chunks you incorporated (by model_id and chunk_type).\n"
        "- Do not mention System B, delta cards, audits, or hidden reasoning.\n"
        "- Do not invent facts beyond the original answer and audit payload.\n\n"
        "QUERY:\n"
        f"{normalize_text(query)}\n\n"
        "ORIGINAL ANSWER:\n"
        f"{normalize_text(vanilla_answer)}\n\n"
        "REASONING AUDIT JSON:\n"
        f"{json.dumps(audit_payload, ensure_ascii=False, indent=2)}\n"
    )


def summarize_boundary_calls(boundary_calls: Sequence[BoundaryCallTrace]) -> dict[str, object]:
    calls = list(boundary_calls or [])
    return {
        "call_count": len(calls),
        "prompt_tokens_total": sum(int(call.prompt_tokens or 0) for call in calls),
        "completion_tokens_total": sum(int(call.completion_tokens or 0) for call in calls),
        "total_tokens_total": sum(int(call.total_tokens or 0) for call in calls),
        "cached_tokens_total": sum(int(call.cached_tokens or 0) for call in calls),
        "cache_write_tokens_total": sum(int(call.cache_write_tokens or 0) for call in calls),
        "reasoning_tokens_total": sum(int(call.reasoning_tokens or 0) for call in calls),
        "cache_hit_call_count": sum(1 for call in calls if int(call.cached_tokens or 0) > 0),
        "reasoning_disabled_all_calls": bool(calls) and all(bool(call.reasoning_disabled) for call in calls),
        "reasoning_leak_detected": any(
            bool(call.reasoning_details_present) or int(call.reasoning_tokens or 0) > 0
            for call in calls
        ),
        "providers": list(dict.fromkeys(normalize_text(call.provider_name) for call in calls if normalize_text(call.provider_name))),
        "models": list(dict.fromkeys(normalize_text(call.model) for call in calls if normalize_text(call.model))),
    }


def compare_expected_focus(
    expected_focus: Sequence[object],
    detected_tendencies: Sequence[object],
    catalog: TendencyCatalog,
) -> dict[str, object]:
    if isinstance(expected_focus, (str, bytes)):
        expected_values = [expected_focus]
    else:
        expected_values = list(expected_focus or [])
    expected_focus_raw = [normalize_text(value) for value in expected_values if normalize_text(value)]
    expected_tendencies: list[str] = []
    noncanonical_expected_focus: list[str] = []
    for raw_value in expected_focus_raw:
        try:
            tendency_id = catalog.lookup(raw_value).tendency_id
        except KeyError:
            noncanonical_expected_focus.append(raw_value)
            continue
        if tendency_id not in expected_tendencies:
            expected_tendencies.append(tendency_id)

    if isinstance(detected_tendencies, (str, bytes)):
        detected_values = [detected_tendencies]
    else:
        detected_values = list(detected_tendencies or [])
    detected = [
        normalize_text(value)
        for value in detected_values
        if normalize_text(value)
    ]
    matched = [tendency_id for tendency_id in expected_tendencies if tendency_id in detected]
    missed = [tendency_id for tendency_id in expected_tendencies if tendency_id not in detected]
    unexpected = [tendency_id for tendency_id in detected if tendency_id not in expected_tendencies]

    expected_count = len(expected_tendencies)
    detected_count = len(detected)
    matched_count = len(matched)
    return {
        "expected_focus_raw": expected_focus_raw,
        "expected_tendencies": expected_tendencies,
        "noncanonical_expected_focus": noncanonical_expected_focus,
        "detected_tendencies": detected,
        "matched_expected_tendencies": matched,
        "missed_expected_tendencies": missed,
        "unexpected_detected_tendencies": unexpected,
        "expected_count": expected_count,
        "matched_count": matched_count,
        "detected_count": detected_count,
        "expected_recall": round(matched_count / expected_count, 3) if expected_count else None,
        "unexpected_rate": round(len(unexpected) / detected_count, 3) if detected_count else None,
        "has_comparable_expectations": bool(expected_tendencies),
    }


def summarize_expectation_comparisons(case_summaries: Sequence[Mapping[str, object]]) -> dict[str, object]:
    cases = list(case_summaries or [])
    comparable_cases = 0
    matched_total = 0
    expected_total = 0
    detected_total = 0
    unexpected_total = 0
    matched_counter: Counter[str] = Counter()
    missed_counter: Counter[str] = Counter()
    unexpected_counter: Counter[str] = Counter()
    noncanonical_counter: Counter[str] = Counter()

    for case in cases:
        comparison = case.get("expectation_comparison", {})
        if not isinstance(comparison, Mapping):
            continue
        expected_tendencies = [
            normalize_text(value)
            for value in list(comparison.get("expected_tendencies", []) or [])
            if normalize_text(value)
        ]
        matched = [
            normalize_text(value)
            for value in list(comparison.get("matched_expected_tendencies", []) or [])
            if normalize_text(value)
        ]
        missed = [
            normalize_text(value)
            for value in list(comparison.get("missed_expected_tendencies", []) or [])
            if normalize_text(value)
        ]
        unexpected = [
            normalize_text(value)
            for value in list(comparison.get("unexpected_detected_tendencies", []) or [])
            if normalize_text(value)
        ]
        noncanonical = [
            normalize_text(value)
            for value in list(comparison.get("noncanonical_expected_focus", []) or [])
            if normalize_text(value)
        ]

        if expected_tendencies:
            comparable_cases += 1
        expected_total += len(expected_tendencies)
        matched_total += len(matched)
        detected_total += len(
            [
                normalize_text(value)
                for value in list(comparison.get("detected_tendencies", []) or [])
                if normalize_text(value)
            ]
        )
        unexpected_total += len(unexpected)
        matched_counter.update(matched)
        missed_counter.update(missed)
        unexpected_counter.update(unexpected)
        noncanonical_counter.update(noncanonical)

    return {
        "cases_with_expectations": sum(
            1
            for case in cases
            if isinstance(case.get("expectation_comparison", {}), Mapping)
            and bool(case.get("expectation_comparison", {}).get("expected_focus_raw"))
        ),
        "comparable_cases": comparable_cases,
        "expected_tendencies_total": expected_total,
        "matched_expected_total": matched_total,
        "missed_expected_total": expected_total - matched_total,
        "detected_tendencies_total": detected_total,
        "unexpected_detected_total": unexpected_total,
        "expected_recall": round(matched_total / expected_total, 3) if expected_total else None,
        "unexpected_rate": round(unexpected_total / detected_total, 3) if detected_total else None,
        "matched_by_tendency": dict(sorted(matched_counter.items())),
        "missed_by_tendency": dict(sorted(missed_counter.items())),
        "unexpected_by_tendency": dict(sorted(unexpected_counter.items())),
        "noncanonical_expected_focus": dict(sorted(noncanonical_counter.items())),
    }


def delta_card_to_payload(delta_card: DeltaCard) -> dict[str, object]:
    return {
        "findings": [_finding_payload(finding) for finding in delta_card.findings],
        "top_findings": [_finding_payload(finding) for finding in delta_card.top_findings],
        "secondary_findings": [
            _finding_payload(finding) for finding in delta_card.presented_secondary_findings
        ],
        "secondary_findings_full": [_finding_payload(finding) for finding in delta_card.secondary_findings],
        "compound_groups": [_compound_payload(compound) for compound in delta_card.compound_groups],
        "top_compound_groups": [
            _compound_payload(compound) for compound in delta_card.top_compound_groups
        ],
        "secondary_compound_groups": [
            _compound_payload(compound) for compound in delta_card.secondary_compound_groups
        ],
        "secondary_summarization_active": delta_card.secondary_summarization_active,
        "secondary_additional_pressures_note": delta_card.secondary_additional_pressures_note,
        "secondary_additional_pressure_count": delta_card.secondary_additional_pressure_count,
        "secondary_additional_pressure_tendency_ids": list(
            delta_card.secondary_additional_pressure_tendency_ids
        ),
        "detected_tendencies": list(delta_card.detected_tendencies),
        "selected_model_ids": list(delta_card.selected_model_ids),
        "challenge_statements": list(delta_card.challenge_statements),
        "next_moves": list(delta_card.next_moves),
        "major_tensions": list(delta_card.major_tensions),
        "top_challenge_statements": list(delta_card.top_challenge_statements),
        "secondary_challenge_statements": list(delta_card.secondary_challenge_statements),
        "top_next_moves": list(delta_card.top_next_moves),
        "secondary_next_moves": list(delta_card.secondary_next_moves),
    }


def companion_card_to_payload(companion_card: CompanionCard | None) -> dict[str, object] | None:
    if companion_card is None:
        return None
    return {
        "detected_models": [
            {
                "model_id": item.model_id,
                "model_name": item.model_name,
                "evidence_quote": item.evidence_quote,
                "presence_mode": item.presence_mode,
                "presence_explanation": item.presence_explanation,
                "detection_confidence": item.detection_confidence,
            }
            for item in companion_card.detected_models
        ],
        "expansions": [
            {
                "source_model_id": item.source_model_id,
                "relation_type": item.relation_type,
                "model_id": item.model_id,
                "model_name": item.model_name,
                "substrate_chunk": item.substrate_chunk,
                "why_relevant": item.why_relevant,
                **({"tension_type": item.tension_type} if item.tension_type is not None else {}),
                **({"affinity_rationale": item.affinity_rationale} if item.affinity_rationale else {}),
                **({"activation_condition": item.activation_condition} if item.activation_condition else {}),
            }
            for item in companion_card.expansions
        ],
        "failure_hints": [
            {
                "source_model_id": item.source_model_id,
                "text": item.text,
                "extraction_type": item.extraction_type,
                "confidence": item.confidence,
            }
            for item in companion_card.failure_hints
        ],
        "heuristic_hints": [
            {
                "source_model_id": item.source_model_id,
                "text": item.text,
                "extraction_type": item.extraction_type,
                "confidence": item.confidence,
            }
            for item in companion_card.heuristic_hints
        ],
        "premortem_hints": [
            {
                "source_model_id": item.source_model_id,
                "text": item.text,
                "extraction_type": item.extraction_type,
                "confidence": item.confidence,
            }
            for item in companion_card.premortem_hints
        ],
        "identity_chunks": [
            {
                "model_id": item.model_id,
                "display_name": item.display_name,
                "select_when": list(item.select_when),
                "danger_when": list(item.danger_when),
                "reasoning_types": list(item.reasoning_types),
                "input_type": item.input_type,
                "output_type": item.output_type,
            }
            for item in companion_card.identity_chunks
        ],
        "detection_model_count": companion_card.detection_model_count,
        "expansion_count": companion_card.expansion_count,
        "failure_hint_count": companion_card.failure_hint_count,
        "heuristic_hint_count": companion_card.heuristic_hint_count,
        "premortem_hint_count": companion_card.premortem_hint_count,
        "identity_chunk_count": companion_card.identity_chunk_count,
        "detection_source": companion_card.detection_source,
    }


def _finding_payload(finding: object) -> dict[str, object]:
    return {
        "tendency_id": getattr(finding, "tendency_id", ""),
        "tendency_name": getattr(finding, "tendency_name", ""),
        "sub_pattern": getattr(finding, "sub_pattern", ""),
        "severity": getattr(finding, "severity", ""),
        "specific_passage": getattr(finding, "specific_passage", ""),
        "challenge_statement": getattr(finding, "challenge_statement", ""),
        "next_move": getattr(finding, "next_move", ""),
        "is_trusted_surface": bool(getattr(finding, "is_trusted_surface", False)),
        "selected_model_ids": list(getattr(finding, "selected_model_ids", ()) or ()),
        "major_tensions": list(getattr(finding, "major_tensions", ()) or ()),
        "intervention_hint": getattr(finding, "intervention_hint", ""),
    }


def _compound_payload(compound: object) -> dict[str, object]:
    return {
        "compound_id": getattr(compound, "compound_id", ""),
        "label": getattr(compound, "label", ""),
        "description": getattr(compound, "description", ""),
        "member_tendency_ids": list(getattr(compound, "member_tendency_ids", ()) or ()),
        "tier": getattr(compound, "tier", ""),
        "findings": [_finding_payload(finding) for finding in getattr(compound, "findings", ()) or ()],
    }
