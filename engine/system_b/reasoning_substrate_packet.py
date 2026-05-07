from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


PACKET_VERSION = "reasoning_substrate_packet.v1"
STATUS = "draft_review_only"
RUNTIME_POLICY = "runtime_dormant"
ALLOWED_COVERAGE_STATUSES = frozenset(
    {
        "reviewed_affordance_available",
        "graph_only_runtime_card",
        "absence_only",
        "missing_reviewed_record",
        "source_too_thin",
        "conflicting_or_weak_support",
    }
)
DEFAULT_BLOCKED_SURFACES = (
    "live_observatory_rendering",
    "memo_integration",
    "step8_integration",
    "step6_integration",
    "lane4_integration",
    "lolla_runtime_use",
    "user_facing_decision_pressure_block",
    "prompt_changes",
    "generation_changes",
    "new_extraction",
    "batch_3b",
    "paid_gate4_reruns_by_default",
)
GRAPH_CONTEXT_FIELDS = (
    "select_when",
    "danger_when",
    "failure_modes",
    "premortem_questions",
    "heuristics",
)
REVIEWED_SNIPPET_FIELDS = (
    "use_when",
    "do_not_use_when",
    "case_evidence_needed",
    "treatment_requirements",
    "diagnostic_questions",
    "misuse_guards",
    "source_evidence",
)


@dataclass(frozen=True)
class CandidateNomination:
    """Explicit review-only nomination for a candidate mental-model shelf."""

    model_id: str
    pulled_by: tuple[str, ...]
    why_pulled: tuple[Mapping[str, Any], ...]
    lane_order: int | None = None
    lane_score: float | None = None


def build_reasoning_substrate_packet_from_files(
    *,
    root: Path,
    packet_id: str,
    transaction_context: Mapping[str, Any],
    nominations: list[CandidateNomination] | tuple[CandidateNomination, ...],
    knowledge_graph_path: Path | None = None,
    affordances_path: Path | None = None,
    source_manifest_path: Path | None = None,
    candidate_card_target_max: int = 12,
    snippet_target_max_per_card: int = 3,
) -> dict[str, Any]:
    root = Path(root)
    knowledge_graph = _load_json(knowledge_graph_path or root / "data" / "knowledge_graph.json")
    affordances = _load_json(
        affordances_path
        or root / "data" / "compiled" / "model_affordances" / "affordances_v4.json"
    )
    source_manifest = _load_json(
        source_manifest_path or root / "data" / "model_sources" / "manifest.json"
    )
    return build_reasoning_substrate_packet(
        packet_id=packet_id,
        transaction_context=transaction_context,
        nominations=nominations,
        knowledge_graph=knowledge_graph,
        affordances=affordances,
        source_manifest=source_manifest,
        source_artifacts=[
            str(knowledge_graph_path or root / "data" / "knowledge_graph.json"),
            str(
                affordances_path
                or root / "data" / "compiled" / "model_affordances" / "affordances_v4.json"
            ),
            str(source_manifest_path or root / "data" / "model_sources" / "manifest.json"),
        ],
        candidate_card_target_max=candidate_card_target_max,
        snippet_target_max_per_card=snippet_target_max_per_card,
    )


def build_reasoning_substrate_packet(
    *,
    packet_id: str,
    transaction_context: Mapping[str, Any],
    nominations: list[CandidateNomination] | tuple[CandidateNomination, ...],
    knowledge_graph: Mapping[str, Any],
    affordances: Mapping[str, Any],
    source_manifest: Mapping[str, Any],
    source_artifacts: list[str] | tuple[str, ...] = (),
    candidate_card_target_max: int = 12,
    snippet_target_max_per_card: int = 3,
) -> dict[str, Any]:
    models = _mapping(knowledge_graph.get("models"))
    reviewed_index = _reviewed_record_index(affordances)
    source_custody = _source_custody_index(source_manifest)

    cards: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []
    seen_model_ids: set[str] = set()
    ordered_nominations = sorted(
        enumerate(nominations),
        key=lambda item: (
            item[1].lane_order if item[1].lane_order is not None else 10**9,
            item[0],
        ),
    )

    for original_index, nomination in ordered_nominations:
        model_id = _slug(nomination.model_id)
        if model_id in seen_model_ids:
            suppressed.append(
                _suppressed_candidate(
                    nomination=nomination,
                    candidate_index=original_index,
                    suppression_reason="duplicate_model_id",
                    coverage_status=_coverage_status_for(model_id, reviewed_index),
                )
            )
            continue
        seen_model_ids.add(model_id)

        model = _mapping(models.get(model_id))
        if not model:
            suppressed.append(
                _suppressed_candidate(
                    nomination=nomination,
                    candidate_index=original_index,
                    suppression_reason="model_id_not_in_runtime_graph",
                    coverage_status="missing_reviewed_record",
                )
            )
            continue

        if len(cards) >= candidate_card_target_max:
            suppressed.append(
                _suppressed_candidate(
                    nomination=nomination,
                    candidate_index=original_index,
                    suppression_reason="packet_cap",
                    coverage_status=_coverage_status_for(model_id, reviewed_index),
                )
            )
            continue

        reviewed_record = reviewed_index.get(model_id)
        coverage_status = _coverage_status_for(model_id, reviewed_index)
        cards.append(
            _candidate_card(
                model_id=model_id,
                model=model,
                nomination=nomination,
                card_index=len(cards),
                coverage_status=coverage_status,
                reviewed_record=reviewed_record,
                source_custody_entry=source_custody.get(model_id),
                snippet_cap=snippet_target_max_per_card,
            )
        )

    return {
        "packet_version": PACKET_VERSION,
        "packet_id": str(packet_id),
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "source_artifacts": list(source_artifacts),
        "transaction_context": dict(transaction_context),
        "candidate_cards": cards,
        "suppressed_candidates": suppressed,
        "coverage_summary": _coverage_summary(cards),
        "packet_policy": {
            "candidate_card_target_min": 0,
            "candidate_card_target_max": candidate_card_target_max,
            "snippet_target_min_per_card": 0,
            "snippet_target_max_per_card": snippet_target_max_per_card,
            "deterministic_role": "validate_package_cap_reference_and_label",
            "semantic_selection_role": "llm_or_reviewer",
            "forbid_public_copy": True,
            "forbid_final_pressure_selection": True,
            "forbid_case_type_templates": True,
        },
        "blocked_surfaces": list(DEFAULT_BLOCKED_SURFACES),
        "review_notes": [
            "Review-only packet built from explicit nominations; no live lanes were run.",
            "Graph-only cards are eligible recall material but not reviewed affordance depth.",
            "LLM or reviewer owns semantic selection, merging, ignoring, and final wording.",
        ],
    }


def _candidate_card(
    *,
    model_id: str,
    model: Mapping[str, Any],
    nomination: CandidateNomination,
    card_index: int,
    coverage_status: str,
    reviewed_record: Mapping[str, Any] | None,
    source_custody_entry: Mapping[str, Any] | None,
    snippet_cap: int,
) -> dict[str, Any]:
    graph_fields = _runtime_graph_fields(model, snippet_cap=snippet_cap)
    has_source_custody = source_custody_entry is not None
    card = {
        "card_id": f"card-{card_index + 1:03d}-{model_id}",
        "model_id": model_id,
        "display_name": str(model.get("display_name") or model.get("name") or model_id),
        "pulled_by": _dedupe_strings(nomination.pulled_by),
        "why_pulled": [dict(item) for item in nomination.why_pulled],
        "coverage_status": coverage_status,
        "source_custody": _source_custody_payload(
            model=model,
            entry=source_custody_entry,
            reviewed_record_available=reviewed_record is not None,
            coverage_status=coverage_status,
        ),
        "runtime_graph_fields": graph_fields,
        "reviewed_affordance_fields": {},
        "absence_records": [],
        "do_not_overclaim": [],
        "llm_instruction": (
            "Consider, merge, set aside, or ignore. Do not force use. "
            "Do not treat coverage labels as final semantic selection."
        ),
    }
    if nomination.lane_order is not None or nomination.lane_score is not None:
        card["nomination_metadata"] = {
            "lane_order": nomination.lane_order,
            "lane_score": nomination.lane_score,
        }

    if reviewed_record is None:
        card["do_not_overclaim"].append(
            "No reviewed affordance record is available in the current corpus."
        )
        return card

    card["absence_records"] = _absence_records(reviewed_record, snippet_cap=snippet_cap)
    if coverage_status in {"reviewed_affordance_available", "conflicting_or_weak_support"}:
        card["reviewed_affordance_fields"] = _reviewed_affordance_fields(
            reviewed_record,
            has_source_custody=has_source_custody,
            snippet_cap=snippet_cap,
        )
    if not has_source_custody:
        card["do_not_overclaim"].append(
            "Reviewed affordance record exists, but reviewed source custody was not found."
        )
    if coverage_status == "source_too_thin":
        card["do_not_overclaim"].append(
            "Reviewed source was marked too thin for strong operational use."
        )
    if coverage_status == "absence_only":
        card["do_not_overclaim"].append(
            "Reviewed material is mainly absence/caution evidence; do not invent an affordance."
        )
    return card


def _runtime_graph_fields(model: Mapping[str, Any], *, snippet_cap: int) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "source_file": str(model.get("source_file", "")),
        "reasoning_types": _dedupe_strings(_list(model.get("reasoning_types"))),
    }
    for field in GRAPH_CONTEXT_FIELDS:
        fields[field] = [
            _compact_graph_item(item)
            for item in _list(model.get(field))[:snippet_cap]
        ]
    return fields


def _reviewed_affordance_fields(
    record: Mapping[str, Any],
    *,
    has_source_custody: bool,
    snippet_cap: int,
) -> dict[str, Any]:
    affordances = [_mapping(item) for item in _list(record.get("affordances"))[:snippet_cap]]
    source_evidence: list[dict[str, Any]] = []
    for affordance in affordances:
        affordance_id = str(affordance.get("affordance_id", ""))
        for evidence in _list(affordance.get("source_evidence"))[:snippet_cap]:
            evidence_payload = dict(_mapping(evidence))
            evidence_payload["affordance_id"] = affordance_id
            evidence_payload["source_custody"] = "reviewed_manifest" if has_source_custody else "missing"
            source_evidence.append(evidence_payload)
            if len(source_evidence) >= snippet_cap:
                break
        if len(source_evidence) >= snippet_cap:
            break

    return {
        "affordance_ids": [
            str(affordance.get("affordance_id"))
            for affordance in affordances
            if str(affordance.get("affordance_id", "")).strip()
        ],
        "use_when": _activation_items(affordances, "use_when", snippet_cap=snippet_cap),
        "do_not_use_when": _activation_items(
            affordances,
            "do_not_use_when",
            snippet_cap=snippet_cap,
        ),
        "case_evidence_needed": _activation_items(
            affordances,
            "case_evidence_needed",
            snippet_cap=snippet_cap,
        ),
        "treatment_requirements": _treatment_requirements(affordances, snippet_cap=snippet_cap),
        "diagnostic_questions": _flat_affordance_items(
            affordances,
            "diagnostic_questions",
            snippet_cap=snippet_cap,
        ),
        "misuse_guards": _flat_affordance_items(
            affordances,
            "misuse_guards",
            snippet_cap=snippet_cap,
        ),
        "source_evidence": source_evidence,
        "confidence": _aggregate_confidence(affordances),
    }


def _activation_items(
    affordances: list[Mapping[str, Any]],
    field: str,
    *,
    snippet_cap: int,
) -> list[str]:
    values: list[str] = []
    for affordance in affordances:
        activation_shape = _mapping(affordance.get("activation_shape"))
        values.extend(_dedupe_strings(_list(activation_shape.get(field))))
    return _dedupe_strings(values)[:snippet_cap]


def _flat_affordance_items(
    affordances: list[Mapping[str, Any]],
    field: str,
    *,
    snippet_cap: int,
) -> list[str]:
    values: list[str] = []
    for affordance in affordances:
        values.extend(_dedupe_strings(_list(affordance.get(field))))
    return _dedupe_strings(values)[:snippet_cap]


def _treatment_requirements(
    affordances: list[Mapping[str, Any]],
    *,
    snippet_cap: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for affordance in affordances:
        for requirement in _list(affordance.get("treatment_requirements")):
            item = _mapping(requirement)
            rows.append(
                {
                    "requirement_id": str(item.get("requirement_id", "")),
                    "description": str(item.get("description", "")),
                    "evidence_required": _dedupe_strings(
                        _list(item.get("evidence_required"))
                    )[:snippet_cap],
                    "good_output_shape": _dedupe_strings(
                        _list(item.get("good_output_shape"))
                    )[:snippet_cap],
                }
            )
            if len(rows) >= snippet_cap:
                return rows
    return rows


def _absence_records(record: Mapping[str, Any], *, snippet_cap: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    model_id = str(record.get("model_id", ""))
    for absence in _list(record.get("absence_records"))[:snippet_cap]:
        item = _mapping(absence)
        rows.append(
            {
                "model_id": model_id,
                "attempted_field": str(item.get("attempted_field", "")),
                "status": str(item.get("status", "")),
                "reason": str(item.get("reason", "")),
                "runtime_policy": str(item.get("runtime_policy", "")),
            }
        )
    return rows


def _coverage_summary(cards: list[Mapping[str, Any]]) -> dict[str, Any]:
    statuses = Counter(str(card.get("coverage_status", "")) for card in cards)
    graph_only = [
        str(card.get("model_id"))
        for card in cards
        if str(card.get("coverage_status")) == "graph_only_runtime_card"
    ]
    missing_reviewed = [
        str(card.get("model_id"))
        for card in cards
        if str(card.get("coverage_status"))
        in {"graph_only_runtime_card", "missing_reviewed_record"}
    ]
    return {
        "candidate_card_count": len(cards),
        "reviewed_card_count": statuses["reviewed_affordance_available"],
        "graph_only_card_count": statuses["graph_only_runtime_card"],
        "absence_only_card_count": statuses["absence_only"],
        "missing_reviewed_record_count": len(missing_reviewed),
        "source_too_thin_count": statuses["source_too_thin"],
        "conflicting_or_weak_support_count": statuses["conflicting_or_weak_support"],
        "missing_reviewed_model_ids": sorted(missing_reviewed),
        "high_value_graph_only_model_ids": sorted(graph_only),
    }


def _suppressed_candidate(
    *,
    nomination: CandidateNomination,
    candidate_index: int,
    suppression_reason: str,
    coverage_status: str,
) -> dict[str, Any]:
    return {
        "candidate_id": f"candidate-{candidate_index + 1:03d}-{_slug(nomination.model_id)}",
        "model_id": _slug(nomination.model_id),
        "suppression_reason": suppression_reason,
        "coverage_status": coverage_status,
        "pulled_by": _dedupe_strings(nomination.pulled_by),
        "why_pulled": [dict(item) for item in nomination.why_pulled],
        "do_not_recover_as_pressure_without_review": True,
    }


def _coverage_status_for(
    model_id: str,
    reviewed_index: Mapping[str, Mapping[str, Any]],
) -> str:
    record = reviewed_index.get(model_id)
    if record is None:
        return "graph_only_runtime_card"
    status = str(record.get("status", ""))
    affordances = _list(record.get("affordances"))
    absence_records = _list(record.get("absence_records"))
    if status == "source_too_thin":
        return "source_too_thin"
    if status in {"weak_support", "deferred_for_review"}:
        return "conflicting_or_weak_support"
    if affordances:
        return "reviewed_affordance_available"
    if absence_records or status in {"not_supported_by_source", "duplicate_of_existing_field"}:
        return "absence_only"
    return "missing_reviewed_record"


def _reviewed_record_index(affordances: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(record.get("model_id")): _mapping(record)
        for record in _list(affordances.get("model_records"))
        if str(_mapping(record).get("model_id", "")).strip()
    }


def _source_custody_index(
    source_manifest: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    return {
        str(item.get("model_id")): _mapping(item)
        for item in _list(source_manifest.get("files"))
        if str(_mapping(item).get("model_id", "")).strip()
    }


def _source_custody_payload(
    *,
    model: Mapping[str, Any],
    entry: Mapping[str, Any] | None,
    reviewed_record_available: bool,
    coverage_status: str,
) -> dict[str, Any]:
    source_file = str(model.get("source_file", ""))
    payload: dict[str, Any] = {
        "custody_status": (
            "repo_source_custodied" if entry is not None else "missing_source_custody"
        ),
        "source_file": source_file,
        "reviewed_record_available": reviewed_record_available,
        "reviewed_affordance_available": (
            coverage_status == "reviewed_affordance_available"
        ),
    }
    if entry is not None:
        payload.update(
            {
                "manifest_path": str(entry.get("path", "")),
                "sha256": str(entry.get("sha256", "")),
                "bytes": int(entry.get("bytes", 0)),
            }
        )
    return payload


def _compact_graph_item(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: str(value.get(key, ""))
            for key in (
                "mode",
                "description",
                "mitigation",
                "source_quote",
                "extraction_type",
                "confidence",
            )
            if str(value.get(key, "")).strip()
        }
    return str(value)


def _aggregate_confidence(affordances: list[Mapping[str, Any]]) -> str:
    confidences = {str(item.get("confidence", "")) for item in affordances}
    if not confidences:
        return ""
    if confidences == {"high"}:
        return "high"
    if "weak" in confidences:
        return "weak"
    if "medium" in confidences:
        return "medium"
    return "mixed"


def _dedupe_strings(values: Any) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _slug(value: str) -> str:
    return str(value or "").strip().replace("_", "-").lower()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
