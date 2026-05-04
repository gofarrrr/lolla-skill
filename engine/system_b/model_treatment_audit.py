from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


TREATMENT_AUDIT_SCHEMA_VERSION = "model_treatment_audit.v2"

TREATMENT_STATUS = frozenset(
    {
        "treated",
        "partially_treated",
        "set_aside_with_reason",
        "duplicate_of_existing_pressure",
        "not_treated",
        "not_applicable",
    }
)
BASELINE_COVERAGE = frozenset(
    {
        "new_finding",
        "duplicate_of_existing_pressure",
        "additional_specificity",
        "not_a_finding",
    }
)
CONFIDENCE = frozenset({"high", "medium", "weak"})
MERGE_GATE_GAP_STATUSES = frozenset(
    {"partially_treated", "not_treated"}
)
MERGE_GATE_BASELINE_CLASSES = frozenset({"new_finding", "additional_specificity"})
ACTIVATION_STATUS = frozenset(
    {
        "activated",
        "not_activated",
        "unclear_activation",
        "set_aside_as_misfit",
        "activation_shape_missing",
    }
)
EVIDENCE_TIER = frozenset(
    {
        "tier_1_net_new_decision_gap",
        "tier_2_additional_operational_specificity",
        "tier_3_duplicate_or_quality_note",
        "excluded",
    }
)
MIN_TREATMENT_NOTE_LENGTH = 40
MIN_ACTIVATION_NOTE_LENGTH = 40
MIN_TREATED_QUOTE_LENGTH = 30


class ModelTreatmentAuditValidationError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ModelTreatmentAuditValidationError(f"{path}: expected JSON object")
    return payload


def load_compiled_affordances(path: Path) -> dict[str, list[dict[str, Any]]]:
    payload = load_json(path)
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in _list(payload.get("affordances")):
        affordance = _mapping(item)
        model_id = str(affordance.get("model_id") or "")
        if model_id:
            by_model[model_id].append(dict(affordance))
    for model_id in by_model:
        by_model[model_id].sort(key=lambda item: str(item.get("affordance_id") or ""))
    return dict(sorted(by_model.items()))


def load_do_not_promote_flags(path: Path) -> dict[str, dict[str, str]]:
    if not Path(path).exists():
        return {}
    flags: dict[str, dict[str, str]] = {}
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        affordance_id = cells[0].strip("`")
        if "." not in affordance_id:
            continue
        flags[affordance_id] = {
            "reason": cells[1],
            "future_trigger_condition": cells[2],
        }
    return flags


def selected_models_by_lane(route_trace: Mapping[str, Any]) -> dict[str, list[str]]:
    lanes = _mapping(route_trace.get("lanes"))
    by_model: dict[str, set[str]] = defaultdict(set)

    lane1 = _mapping(lanes.get("lane1"))
    for route in (_mapping(item) for item in _list(lane1.get("routes"))):
        for model_id in _list(route.get("selected_model_ids")):
            if model_id:
                by_model[str(model_id)].add("lane1")

    lane2 = _mapping(lanes.get("lane2"))
    for model_id in _list(lane2.get("selected_model_ids")):
        if model_id:
            by_model[str(model_id)].add("lane2")

    lane3 = _mapping(lanes.get("lane3"))
    for route in (_mapping(item) for item in _list(lane3.get("routes"))):
        for model_id in _list(route.get("selected_model_ids")):
            if model_id:
                by_model[str(model_id)].add("lane3")

    lane4 = _mapping(lanes.get("lane4"))
    for route in (_mapping(item) for item in _list(lane4.get("routes"))):
        for model_id in _list(route.get("selected_model_ids")):
            if model_id:
                by_model[str(model_id)].add("lane4")

    return {model_id: sorted(lanes) for model_id, lanes in sorted(by_model.items())}


def build_case_context(result: Mapping[str, Any]) -> str:
    query = str(result.get("query") or "").strip()
    if query:
        return query
    extraction = _mapping(result.get("extraction"))
    parts = []
    for key in ("decision_situation", "original_framing"):
        value = str(extraction.get(key) or "").strip()
        if value:
            parts.append(value)
    for item in _list(extraction.get("live_constraints"))[:8]:
        row = _mapping(item)
        text = str(row.get("constraint") or "").strip()
        if text:
            parts.append(f"- {text}")
    return "\n".join(parts)


def build_pressure_baseline_text(result: Mapping[str, Any], run_dir: Path | None = None) -> str:
    parts: list[str] = []
    for key, label in (
        ("gap_check_summary", "Persisted Pressure Check summary"),
        ("memo_pressure_check", "Memo pressure check"),
    ):
        value = str(result.get(key) or "").strip()
        if value:
            parts.append(f"{label}:\n{value}")

    gap_check = _load_gap_check(result, run_dir)
    lanes = _gap_check_lanes(gap_check)
    if lanes:
        lane_lines = ["Structured Pressure Check divergences:"]
        for lane in lanes:
            status = str(lane.get("status") or "")
            lane_name = str(lane.get("lane_name") or "")
            lane_number = lane.get("lane_number", "")
            divergences = _list(lane.get("divergences"))
            if not divergences:
                lane_lines.append(f"- Lane {lane_number} {lane_name}: {status}; no divergences.")
                continue
            lane_lines.append(f"- Lane {lane_number} {lane_name}: {status}")
            for divergence in (_mapping(item) for item in divergences):
                q = divergence.get("question_number", "")
                desc = str(divergence.get("description") or "").strip()
                if desc:
                    lane_lines.append(f"  - Q{q}: {desc}")
        parts.append("\n".join(lane_lines))

    return "\n\n".join(parts).strip() or "No persisted Pressure Check material was available for this archived run."


def build_audited_output_text(result: Mapping[str, Any], run_dir: Path | None = None) -> str:
    sections: list[tuple[str, str]] = []

    revised = _first_file_or_field(run_dir, "revised.txt", result, "revised_answer")
    if revised:
        sections.append(("Revised Answer", revised))

    memo = _read_optional_file(run_dir, "memo.md")
    if memo:
        sections.append(("Memo", memo))

    pressure = build_pressure_baseline_text(result, run_dir)
    if pressure:
        sections.append(("Pressure Check Baseline", pressure))

    card_text = build_audit_surface_text(result)
    if card_text:
        sections.append(("Audit Surfaces", card_text))

    return "\n\n".join(f"## {title}\n{text.strip()}" for title, text in sections if text.strip())


def build_audit_surface_text(result: Mapping[str, Any]) -> str:
    parts: list[str] = []
    delta = _mapping(result.get("delta_card"))
    findings = _list(delta.get("findings")) or [
        *_list(delta.get("top_findings")),
        *_list(delta.get("secondary_findings")),
    ]
    if findings:
        parts.append("Lane 1 findings:")
        for finding in (_mapping(item) for item in findings):
            tendency = str(finding.get("tendency_id") or "").strip()
            models = ", ".join(str(v) for v in _list(finding.get("selected_model_ids")))
            challenge = str(finding.get("challenge_statement") or "").strip()
            next_move = str(finding.get("next_move") or "").strip()
            passage = str(finding.get("specific_passage") or "").strip()
            parts.append(f"- {tendency} [{models}]")
            if passage:
                parts.append(f"  Evidence: {passage}")
            if challenge:
                parts.append(f"  Challenge: {challenge}")
            if next_move:
                parts.append(f"  Next move: {next_move}")

    companion = _mapping(result.get("companion_cheat_sheet"))
    anchors = _list(companion.get("anchors"))
    if anchors:
        parts.append("Lane 2 companion anchors:")
        for anchor in (_mapping(item) for item in anchors):
            model_id = str(anchor.get("model_id") or "").strip()
            quote = str(anchor.get("evidence_quote") or "").strip()
            explanation = str(anchor.get("presence_explanation") or "").strip()
            mode = str(anchor.get("presence_mode") or "").strip()
            parts.append(f"- {model_id} ({mode})")
            if quote:
                parts.append(f"  Evidence: {quote}")
            if explanation:
                parts.append(f"  Explanation: {explanation}")

    frame = _mapping(result.get("frame_pressure_card"))
    reframings = _list(frame.get("reframings"))
    if reframings:
        parts.append("Lane 3 frame reframings:")
        for item in (_mapping(row) for row in reframings):
            model_id = str(item.get("grounding_model") or "").strip()
            question = str(item.get("reframed_question") or "").strip()
            opens = str(item.get("what_opens") or "").strip()
            parts.append(f"- {model_id}: {question}")
            if opens:
                parts.append(f"  Opens: {opens}")

    coverage = _mapping(result.get("structural_coverage_card"))
    gap_questions = {
        str(item.get("dimension_id") or ""): _mapping(item)
        for item in (_mapping(row) for row in _list(coverage.get("gap_questions")))
    }
    gap_routes = _list(coverage.get("gap_routes"))
    if gap_routes:
        parts.append("Lane 4 structural gap routes:")
        for route in (_mapping(item) for item in gap_routes):
            dimension_id = str(route.get("dimension_id") or "")
            dimension_name = str(route.get("dimension_name") or "")
            models = ", ".join(str(v) for v in _list(route.get("candidate_model_ids")))
            parts.append(f"- {dimension_name} [{dimension_id}] -> {models}")
            questions = _list(gap_questions.get(dimension_id, {}).get("questions"))
            for question in questions:
                parts.append(f"  Question: {question}")

    return "\n".join(parts)


def build_model_output_slice(
    result: Mapping[str, Any],
    *,
    model_id: str,
    run_dir: Path | None = None,
) -> str:
    sections: list[tuple[str, str]] = []

    revised = _first_file_or_field(run_dir, "revised.txt", result, "revised_answer")
    if revised:
        sections.append(("Revised Answer", revised))

    pressure = build_pressure_baseline_text(result, run_dir)
    if pressure:
        sections.append(("Pressure Check Baseline", pressure))

    model_surface = build_model_surface_text(result, model_id=model_id)
    if model_surface:
        sections.append((f"Model-Specific Audit Surfaces For {model_id}", model_surface))

    if not model_surface:
        all_surfaces = build_audit_surface_text(result)
        if all_surfaces:
            sections.append(("Audit Surfaces", all_surfaces))

    return "\n\n".join(f"## {title}\n{text.strip()}" for title, text in sections if text.strip())


def build_model_surface_text(result: Mapping[str, Any], *, model_id: str) -> str:
    parts: list[str] = []
    delta = _mapping(result.get("delta_card"))
    findings = _list(delta.get("findings")) or [
        *_list(delta.get("top_findings")),
        *_list(delta.get("secondary_findings")),
    ]
    for finding in (_mapping(item) for item in findings):
        if model_id not in _list(finding.get("selected_model_ids")):
            continue
        tendency = str(finding.get("tendency_id") or "").strip()
        parts.append(f"Lane 1 finding for {model_id}: {tendency}")
        for label, key in (
            ("Evidence", "specific_passage"),
            ("Challenge", "challenge_statement"),
            ("Next move", "next_move"),
        ):
            value = str(finding.get(key) or "").strip()
            if value:
                parts.append(f"{label}: {value}")

    companion = _mapping(result.get("companion_cheat_sheet"))
    for anchor in (_mapping(item) for item in _list(companion.get("anchors"))):
        if str(anchor.get("model_id") or "") != model_id:
            continue
        parts.append(f"Lane 2 companion anchor for {model_id}:")
        for label, key in (
            ("Evidence", "evidence_quote"),
            ("Explanation", "presence_explanation"),
            ("Mode", "presence_mode"),
        ):
            value = str(anchor.get(key) or "").strip()
            if value:
                parts.append(f"{label}: {value}")

    frame = _mapping(result.get("frame_pressure_card"))
    for reframing in (_mapping(item) for item in _list(frame.get("reframings"))):
        if str(reframing.get("grounding_model") or "") != model_id:
            continue
        question = str(reframing.get("reframed_question") or "").strip()
        opens = str(reframing.get("what_opens") or "").strip()
        parts.append(f"Lane 3 reframing for {model_id}: {question}")
        if opens:
            parts.append(f"Opens: {opens}")

    coverage = _mapping(result.get("structural_coverage_card"))
    gap_questions = {
        str(item.get("dimension_id") or ""): _mapping(item)
        for item in (_mapping(row) for row in _list(coverage.get("gap_questions")))
    }
    for route in (_mapping(item) for item in _list(coverage.get("gap_routes"))):
        if model_id not in _list(route.get("candidate_model_ids")):
            continue
        dimension_id = str(route.get("dimension_id") or "")
        dimension_name = str(route.get("dimension_name") or "")
        parts.append(f"Lane 4 structural gap route for {model_id}: {dimension_name}")
        for question in _list(gap_questions.get(dimension_id, {}).get("questions")):
            parts.append(f"Question: {question}")

    return "\n".join(parts)


def build_summary_payload(audits: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    status_counts: Counter[str] = Counter()
    activation_counts: Counter[str] = Counter()
    baseline_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    tier_counts: Counter[str] = Counter()
    model_counts: Counter[str] = Counter()
    lane_counts: Counter[str] = Counter()
    new_findings: list[dict[str, Any]] = []
    duplicate_examples: list[dict[str, Any]] = []
    judge_rejection_count = 0
    token_totals: Counter[str] = Counter()

    for audit in audits:
        run_id = str(audit.get("run_id") or "")
        judge_rejection_count += int(_mapping(audit.get("validation_summary")).get("judge_rejection_count") or 0)
        metadata = _mapping(audit.get("metadata"))
        usage = _mapping(metadata.get("token_usage"))
        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
            token_totals[key] += int(usage.get(key) or 0)
        for item in (_mapping(row) for row in _list(audit.get("items"))):
            model_id = str(item.get("model_id") or "")
            status = str(item.get("treatment_status") or "")
            activation = str(item.get("activation_status") or "")
            baseline = str(item.get("baseline_coverage") or "")
            confidence = str(item.get("confidence") or "")
            tier = compute_evidence_tier(item)
            status_counts[status] += 1
            activation_counts[activation] += 1
            baseline_counts[baseline] += 1
            confidence_counts[confidence] += 1
            tier_counts[tier] += 1
            model_counts[model_id] += 1
            for lane in _list(item.get("selected_lanes")):
                lane_counts[str(lane)] += 1
            if item_is_merge_gate_candidate(item):
                new_findings.append(
                    {
                        "run_id": run_id,
                        "model_id": model_id,
                        "affordance_id": item.get("affordance_id", ""),
                        "treatment_status": status,
                        "activation_status": activation,
                        "baseline_coverage": baseline,
                        "evidence_tier": tier,
                        "one_line_description": item.get("one_line_description", ""),
                        "treatment_note": item.get("treatment_note", ""),
                    }
                )
            if baseline == "duplicate_of_existing_pressure":
                duplicate_examples.append(
                    {
                        "run_id": run_id,
                        "model_id": model_id,
                        "affordance_id": item.get("affordance_id", ""),
                        "treatment_status": status,
                        "treatment_note": item.get("treatment_note", ""),
                    }
                )

    return {
        "schema_version": TREATMENT_AUDIT_SCHEMA_VERSION,
        "audited_run_count": len(audits),
        "audited_item_count": sum(len(_list(audit.get("items"))) for audit in audits),
        "treatment_status_distribution": dict(sorted(status_counts.items())),
        "activation_status_distribution": dict(sorted(activation_counts.items())),
        "baseline_coverage_distribution": dict(sorted(baseline_counts.items())),
        "evidence_tier_distribution": dict(sorted(tier_counts.items())),
        "confidence_distribution": dict(sorted(confidence_counts.items())),
        "per_model_audit_counts": dict(sorted(model_counts.items())),
        "per_lane_audit_counts": dict(sorted(lane_counts.items())),
        "new_finding_count": len(new_findings),
        "new_findings": new_findings,
        "duplicate_of_existing_pressure_count": baseline_counts["duplicate_of_existing_pressure"],
        "duplicate_examples": duplicate_examples,
        "judge_rejection_count": judge_rejection_count,
        "token_usage": dict(sorted(token_totals.items())),
    }


def normalize_judge_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    activation = str(payload.get("activation_status") or "").strip()
    status = str(payload.get("treatment_status") or "").strip()
    if status == "duplicate_existing_pressure":
        status = "duplicate_of_existing_pressure"
    baseline = str(payload.get("baseline_coverage") or "").strip()
    if not baseline:
        baseline = (
            "duplicate_of_existing_pressure"
            if bool(payload.get("duplicate_of_existing_pressure"))
            else "not_a_finding"
        )
    if baseline == "duplicate_existing_pressure":
        baseline = "duplicate_of_existing_pressure"
    return {
        "activation_status": activation,
        "activation_note": str(payload.get("activation_note") or "").strip(),
        "activation_quote": str(payload.get("activation_quote") or ""),
        "treatment_status": status,
        "output_quote": str(payload.get("output_quote") or ""),
        "treatment_note": str(payload.get("treatment_note") or "").strip(),
        "missing_requirements": [
            str(item).strip()
            for item in _list(payload.get("missing_requirements"))
            if str(item).strip()
        ],
        "duplicate_of_existing_pressure": bool(
            payload.get("duplicate_of_existing_pressure")
            or status == "duplicate_of_existing_pressure"
            or baseline == "duplicate_of_existing_pressure"
        ),
        "baseline_coverage": baseline,
        "confidence": str(payload.get("confidence") or "").strip(),
        "one_line_description": str(payload.get("one_line_description") or "").strip(),
    }


def validate_judge_payload(
    payload: Mapping[str, Any],
    *,
    audited_output: str,
    activation_context: str = "",
) -> list[str]:
    item = normalize_judge_payload(payload)
    item["model_id"] = "judge-response"
    item["affordance_id"] = "judge-response.affordance"
    item["do_not_promote_without_rewrite_review"] = False
    item["evidence_tier"] = compute_evidence_tier(item)
    return _item_errors(
        item,
        audited_output=audited_output,
        activation_context=activation_context,
        path="<judge_response>",
    )


def validate_treatment_audit_payload(payload: Mapping[str, Any]) -> None:
    errors = list(iter_treatment_audit_errors(payload))
    if errors:
        raise ModelTreatmentAuditValidationError("; ".join(errors))


def iter_treatment_audit_errors(payload: Mapping[str, Any]) -> Iterable[str]:
    required = (
        "schema_version",
        "run_id",
        "case_id",
        "source_run_ref",
        "metadata",
        "audited_output",
        "pressure_check_baseline",
        "items",
        "validation_summary",
    )
    for key in required:
        if key not in payload:
            yield f"<audit>: missing {key}"
    if any(key not in payload for key in required):
        return

    if payload.get("schema_version") != TREATMENT_AUDIT_SCHEMA_VERSION:
        yield "<audit>: unknown schema_version"
    audited_output = str(payload.get("audited_output") or "")
    if len(audited_output) < 80:
        yield "<audit>: audited_output is too short for quote validation"
    activation_context = str(payload.get("case_context") or "")
    items = payload.get("items")
    if not isinstance(items, list):
        yield "<audit>: items must be a list"
        return
    for index, item in enumerate(items):
        item_payload = _mapping(item)
        quote_scope = str(item_payload.get("audited_output_slice") or audited_output)
        yield from _item_errors(
            item_payload,
            audited_output=quote_scope,
            activation_context=activation_context,
            path=f"items[{index}]",
        )


def item_is_merge_gate_candidate(item: Mapping[str, Any]) -> bool:
    return compute_evidence_tier(item) == "tier_1_net_new_decision_gap"


def compute_evidence_tier(item: Mapping[str, Any]) -> str:
    if bool(item.get("do_not_promote_without_rewrite_review")):
        return "excluded"
    if str(item.get("activation_status") or "") != "activated":
        return "excluded"

    status = str(item.get("treatment_status") or "")
    baseline = str(item.get("baseline_coverage") or "")
    if status in MERGE_GATE_GAP_STATUSES and baseline == "new_finding":
        return "tier_1_net_new_decision_gap"
    if status in MERGE_GATE_GAP_STATUSES and baseline == "additional_specificity":
        return "tier_2_additional_operational_specificity"
    if status == "duplicate_of_existing_pressure" or baseline == "duplicate_of_existing_pressure":
        return "tier_3_duplicate_or_quality_note"
    return "excluded"


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _item_errors(
    item: Mapping[str, Any],
    *,
    audited_output: str,
    activation_context: str = "",
    path: str,
) -> list[str]:
    errors: list[str] = []
    required = (
        "model_id",
        "affordance_id",
        "activation_status",
        "activation_note",
        "activation_quote",
        "treatment_status",
        "output_quote",
        "treatment_note",
        "missing_requirements",
        "duplicate_of_existing_pressure",
        "baseline_coverage",
        "confidence",
        "evidence_tier",
    )
    for key in required:
        if key not in item:
            errors.append(f"{path}: missing {key}")
    if errors:
        return errors

    activation = str(item.get("activation_status") or "")
    if activation not in ACTIVATION_STATUS:
        errors.append(f"{path}: unknown activation_status '{activation}'")

    status = str(item.get("treatment_status") or "")
    if status not in TREATMENT_STATUS:
        errors.append(f"{path}: unknown treatment_status '{status}'")

    baseline = str(item.get("baseline_coverage") or "")
    if baseline not in BASELINE_COVERAGE:
        errors.append(f"{path}: unknown baseline_coverage '{baseline}'")

    confidence = str(item.get("confidence") or "")
    if confidence not in CONFIDENCE:
        errors.append(f"{path}: unknown confidence '{confidence}'")

    tier = str(item.get("evidence_tier") or "")
    if tier not in EVIDENCE_TIER:
        errors.append(f"{path}: unknown evidence_tier '{tier}'")
    expected_tier = compute_evidence_tier(item)
    if tier != expected_tier:
        errors.append(f"{path}: evidence_tier '{tier}' should be '{expected_tier}'")

    activation_quote = str(item.get("activation_quote") or "")
    activation_scope = activation_context or audited_output
    if activation_quote and activation_quote not in activation_scope:
        errors.append(f"{path}: activation_quote is not an exact substring of case_context")
    if activation == "activated" and not activation_quote:
        errors.append(f"{path}: activation_status 'activated' requires activation_quote")

    activation_note = str(item.get("activation_note") or "").strip()
    if len(activation_note) < MIN_ACTIVATION_NOTE_LENGTH:
        errors.append(f"{path}: activation_note shorter than {MIN_ACTIVATION_NOTE_LENGTH} chars")

    if activation == "set_aside_as_misfit" and status != "set_aside_with_reason":
        errors.append(f"{path}: set_aside_as_misfit requires treatment_status set_aside_with_reason")
    if status == "set_aside_with_reason" and activation != "set_aside_as_misfit":
        errors.append(f"{path}: treatment_status set_aside_with_reason requires activation_status set_aside_as_misfit")
    if activation in {"not_activated", "unclear_activation", "activation_shape_missing"} and status != "not_applicable":
        errors.append(f"{path}: activation_status '{activation}' requires treatment_status not_applicable")
    if status in MERGE_GATE_GAP_STATUSES and activation != "activated":
        errors.append(f"{path}: treatment_status '{status}' requires activation_status activated")

    quote = str(item.get("output_quote") or "")
    if quote and quote not in audited_output:
        errors.append(f"{path}: output_quote is not an exact substring of audited_output")
    if status in {
        "treated",
        "partially_treated",
        "set_aside_with_reason",
        "duplicate_of_existing_pressure",
    } and not quote:
        errors.append(f"{path}: treatment_status '{status}' requires output_quote")
    if status == "treated" and len(quote.strip()) < MIN_TREATED_QUOTE_LENGTH:
        errors.append(f"{path}: treated output_quote is shorter than {MIN_TREATED_QUOTE_LENGTH} chars")

    note = str(item.get("treatment_note") or "").strip()
    if len(note) < MIN_TREATMENT_NOTE_LENGTH:
        errors.append(f"{path}: treatment_note shorter than {MIN_TREATMENT_NOTE_LENGTH} chars")

    missing = item.get("missing_requirements")
    if not isinstance(missing, list) or any(not isinstance(value, str) for value in missing):
        errors.append(f"{path}: missing_requirements must be a list of strings")

    if not isinstance(item.get("duplicate_of_existing_pressure"), bool):
        errors.append(f"{path}: duplicate_of_existing_pressure must be boolean")

    return errors


def _load_gap_check(result: Mapping[str, Any], run_dir: Path | None) -> Any:
    if result.get("gap_check") is not None:
        return result.get("gap_check")
    if run_dir is None:
        return None
    path = Path(run_dir) / "gapcheck_lanes.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _gap_check_lanes(gap_check: Any) -> list[Mapping[str, Any]]:
    if isinstance(gap_check, Mapping):
        lanes = gap_check.get("lanes")
        if isinstance(lanes, list):
            return [_mapping(item) for item in lanes]
    if isinstance(gap_check, list):
        return [_mapping(item) for item in gap_check]
    return []


def _first_file_or_field(
    run_dir: Path | None,
    filename: str,
    result: Mapping[str, Any],
    field: str,
) -> str:
    text = _read_optional_file(run_dir, filename)
    if text:
        return text
    return str(result.get(field) or "").strip()


def _read_optional_file(run_dir: Path | None, filename: str) -> str:
    if run_dir is None:
        return ""
    path = Path(run_dir) / filename
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
