from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BEVELIN_AUDIT_SCHEMA_VERSION = "bevelin_lane1_audit.v1"
BEVELIN_COLLECTION_SCHEMA_VERSION = "bevelin_lane1_audit_collection.v1"


@dataclass(frozen=True)
class ProbeSpec:
    probe_id: str
    label: str
    helps_with: str
    win_condition: str
    related_tendencies: tuple[str, ...]
    model_ids: tuple[str, ...]
    effect_types: tuple[str, ...]
    terms: tuple[str, ...]
    single_term_hits: tuple[str, ...] = ()


BEVELIN_PROBES: tuple[ProbeSpec, ...] = (
    ProbeSpec(
        probe_id="representative_evidence",
        label="Representative Evidence",
        helps_with=(
            "Tests whether a vivid case, anecdote, or hopeful signal is being treated as enough evidence."
        ),
        win_condition=(
            "The output asks for a denominator, base rate, sample quality, track record, or falsifying evidence "
            "before treating the claim as decision-grade."
        ),
        related_tendencies=(
            "availability-misweighing-tendency",
            "overoptimism-tendency",
            "social-proof-tendency",
            "reason-respecting-tendency",
        ),
        model_ids=(
            "base-rates",
            "statistics-concepts",
            "statistical-discipline",
            "law-of-large-numbers",
            "survivorship-bias",
            "false-precision-avoidance",
            "scientific-method-evidence-testing",
            "falsifiability",
            "wysiati",
        ),
        effect_types=("evidence_gate", "overclaim_blocker"),
        terms=(
            "base rate",
            "reference class",
            "denominator",
            "sample",
            "sample size",
            "representative",
            "track record",
            "validate",
            "validation",
            "test result",
            "pre-buy",
            "failed cases",
        ),
        single_term_hits=(
            "denominator",
            "representative",
            "validation",
        ),
    ),
    ProbeSpec(
        probe_id="actor_incentives",
        label="Actor Incentives",
        helps_with=(
            "Checks who benefits, who pays, who can game the system, and whether advice respects incentives."
        ),
        win_condition=(
            "The output names incentive gradients, responsibility, accountability, or principal-agent tension "
            "where those forces could distort behavior."
        ),
        related_tendencies=(
            "reward-and-punishment-superresponse-tendency",
            "authority-misinfluence-tendency",
            "reciprocation-tendency",
            "kantian-fairness-tendency",
        ),
        model_ids=(
            "incentives",
            "principal-agent-problem",
            "moral-hazard",
            "obligations-controls-mapping",
            "systems-thinking",
            "game-theory-payoffs",
            "power-dynamics",
        ),
        effect_types=("hidden_assumption", "evidence_gate"),
        terms=(
            "incentive",
            "who benefits",
            "who pays",
            "reward",
            "punishment",
            "measured",
            "responsible",
            "accountable",
            "principal-agent",
            "alignment",
            "gaming",
            "compensation",
            "self-interest",
        ),
        single_term_hits=(
            "incentive",
            "principal-agent",
            "gaming",
            "compensation",
            "self-interest",
        ),
    ),
    ProbeSpec(
        probe_id="downside_reversibility",
        label="Downside And Reversibility",
        helps_with=(
            "Forces optimistic recommendations to state what happens if the decision is wrong or hard to unwind."
        ),
        win_condition=(
            "The output names downside, rollback, stop rules, exit paths, switching costs, or failure conditions."
        ),
        related_tendencies=(
            "overoptimism-tendency",
            "inconsistency-avoidance-tendency",
            "deprival-superreaction-tendency",
            "simple-pain-avoiding-psychological-denial-tendency",
            "stress-influence-tendency",
        ),
        model_ids=(
            "premortem",
            "risk-assessment",
            "switching-costs",
            "optionality",
            "decision-trees",
            "margin-of-safety",
            "resilience",
            "redundancy",
            "risk-vs-uncertainty",
        ),
        effect_types=("executable_test", "uncertainty_boundary", "overclaim_blocker"),
        terms=(
            "downside",
            "reversibility",
            "reverse",
            "exit",
            "stop rule",
            "kill criteria",
            "failure",
            "worst case",
            "if wrong",
            "rollback",
            "unwind",
            "commitment",
            "switching cost",
            "runway",
        ),
        single_term_hits=(
            "downside",
            "reversibility",
            "stop rule",
            "kill criteria",
            "worst case",
            "rollback",
            "switching cost",
            "runway",
        ),
    ),
    ProbeSpec(
        probe_id="absolute_yardstick",
        label="Absolute Yardstick",
        helps_with=(
            "Blocks contrast effects by asking what standard would count as good enough independent of the comparison."
        ),
        win_condition=(
            "The output states a measurable threshold, bar, pass/fail criterion, or absolute standard."
        ),
        related_tendencies=(
            "contrast-misreaction-tendency",
            "overoptimism-tendency",
            "reason-respecting-tendency",
        ),
        model_ids=(
            "goal-setting",
            "metrics",
            "false-precision-avoidance",
            "baseline-establishment",
            "multi-criteria-decision-analysis",
        ),
        effect_types=("evidence_gate", "executable_test", "uncertainty_boundary"),
        terms=(
            "yardstick",
            "threshold",
            "absolute",
            "measure",
            "metric",
            "progress",
            "criteria",
            "criterion",
            "standard",
            "bar",
            "pass/fail",
            "good enough",
        ),
        single_term_hits=(
            "yardstick",
            "threshold",
            "criteria",
            "criterion",
            "pass/fail",
        ),
    ),
    ProbeSpec(
        probe_id="alternatives_opportunity_cost",
        label="Alternatives And Opportunity Cost",
        helps_with=(
            "Prevents false closure by keeping the live option set and next-best alternative visible."
        ),
        win_condition=(
            "The output preserves alternatives, names opportunity cost, or compares the recommendation against "
            "a viable fallback."
        ),
        related_tendencies=(
            "doubt-avoidance-tendency",
            "inconsistency-avoidance-tendency",
            "deprival-superreaction-tendency",
        ),
        model_ids=(
            "optionality",
            "opportunity-cost",
            "decision-trees",
            "batna",
            "counterfactual-reasoning",
            "problem-framing-and-reframing",
            "brainstorming",
        ),
        effect_types=("missing_option", "hidden_assumption"),
        terms=(
            "alternative",
            "option set",
            "opportunity cost",
            "next best",
            "fallback",
            "batna",
            "hybrid",
            "preserve option",
            "tradeoff",
        ),
        single_term_hits=(
            "alternative",
            "opportunity cost",
            "next best",
            "fallback",
            "batna",
            "hybrid",
        ),
    ),
    ProbeSpec(
        probe_id="disconfirmation",
        label="Disconfirmation",
        helps_with=(
            "Turns Munger-style misjudgment detection into a concrete search for what would prove the claim wrong."
        ),
        win_condition=(
            "The output asks for contrary evidence, falsification, a counterargument, an assumption check, or a "
            "test that could invalidate the recommendation."
        ),
        related_tendencies=(
            "inconsistency-avoidance-tendency",
            "reason-respecting-tendency",
            "overoptimism-tendency",
            "simple-pain-avoiding-psychological-denial-tendency",
        ),
        model_ids=(
            "falsifiability",
            "inversion",
            "confirmation-bias",
            "scientific-method-evidence-testing",
            "critical-thinking",
            "premortem",
        ),
        effect_types=("evidence_gate", "executable_test", "overclaim_blocker"),
        terms=(
            "disconfirm",
            "falsify",
            "prove wrong",
            "counterargument",
            "contrary",
            "evidence against",
            "assumption check",
            "invalidate",
        ),
        single_term_hits=(
            "disconfirm",
            "falsify",
            "prove wrong",
            "counterargument",
            "contrary",
            "evidence against",
            "assumption check",
            "invalidate",
        ),
    ),
    ProbeSpec(
        probe_id="state_of_mind",
        label="State Of Mind",
        helps_with=(
            "Checks whether pressure, fear, relief, fatigue, or urgency is shaping the decision more than evidence."
        ),
        win_condition=(
            "The output names the actor's state, slows the decision, or separates emotional pressure from the "
            "decision standard."
        ),
        related_tendencies=(
            "stress-influence-tendency",
            "doubt-avoidance-tendency",
            "liking-loving-tendency",
            "disliking-hating-tendency",
            "simple-pain-avoiding-psychological-denial-tendency",
        ),
        model_ids=(
            "emotional-intelligence",
            "system-2-thinking",
            "checklists",
            "self-control",
            "psychological-safety",
        ),
        effect_types=("uncertainty_boundary", "hidden_assumption", "overclaim_blocker"),
        terms=(
            "stress",
            "fear",
            "afraid",
            "urgency",
            "tired",
            "embarrassed",
            "relief",
            "emotional",
            "emotional pressure",
            "state of mind",
            "deadline",
            "pause",
            "anxiety",
        ),
        single_term_hits=(
            "stress",
            "fear",
            "afraid",
            "urgency",
            "emotional",
            "state of mind",
            "anxiety",
        ),
    ),
    ProbeSpec(
        probe_id="role_reversal_system",
        label="Role Reversal And System Fairness",
        helps_with=(
            "Checks whether the advice would still look fair, controllable, and responsible if roles were reversed."
        ),
        win_condition=(
            "The output names role reversal, decision rights, boundaries, controls, ownership, or fairness of the rule."
        ),
        related_tendencies=(
            "kantian-fairness-tendency",
            "reciprocation-tendency",
            "reward-and-punishment-superresponse-tendency",
            "authority-misinfluence-tendency",
        ),
        model_ids=(
            "power-dynamics",
            "boundaries",
            "obligations-controls-mapping",
            "psychological-safety",
            "principal-agent-problem",
            "systems-thinking",
        ),
        effect_types=("hidden_assumption", "evidence_gate"),
        terms=(
            "role reversed",
            "roles reversed",
            "fairness",
            "ownership",
            "decision rights",
            "boundary",
            "boundaries",
            "rule",
            "enforcement",
            "reciprocate",
            "other side",
        ),
        single_term_hits=(
            "role reversed",
            "roles reversed",
            "fairness",
            "decision rights",
            "boundaries",
            "enforcement",
            "reciprocate",
            "other side",
        ),
    ),
    ProbeSpec(
        probe_id="postmortem_learning",
        label="Postmortem Learning",
        helps_with=(
            "Makes the decision auditable so future feedback can improve the mental model instead of disappearing."
        ),
        win_condition=(
            "The output asks for a record, checkpoint, after-action review, trigger, or monitoring loop."
        ),
        related_tendencies=(
            "use-it-or-lose-it-tendency",
            "inconsistency-avoidance-tendency",
            "overoptimism-tendency",
        ),
        model_ids=(
            "feedback-loops",
            "auditability-traceability",
            "hindsight-bias",
            "iteration",
            "lean-startup-methodology",
            "adaptation",
        ),
        effect_types=("executable_test", "uncertainty_boundary"),
        terms=(
            "postmortem",
            "record",
            "track",
            "feedback loop",
            "checkpoint",
            "after action",
            "monitor",
            "trigger",
        ),
        single_term_hits=(
            "postmortem",
            "feedback loop",
            "checkpoint",
            "after action",
        ),
    ),
)


def load_result(path: Path | str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected JSON object")
    return payload


def build_bevelin_lane1_audit(
    result: Mapping[str, Any],
    *,
    result_path: Path | str | None = None,
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Build a deterministic Bevelin/Lane 1 observability audit for one run."""

    resolved_result_path = Path(result_path) if result_path is not None else None
    resolved_run_dir = _resolve_run_dir(resolved_result_path, run_dir)
    runtime_map = build_runtime_map(result)
    lane1 = build_lane1_summary(result)
    surfaces = build_surface_bundle(result, run_dir=resolved_run_dir)

    probe_results = [
        evaluate_probe(spec, result, surfaces=surfaces, lane1_summary=lane1)
        for spec in BEVELIN_PROBES
    ]
    win_signals = build_win_signals(probe_results, lane1)

    return {
        "schema_version": BEVELIN_AUDIT_SCHEMA_VERSION,
        "source": {
            "result_path": str(resolved_result_path) if resolved_result_path else "",
            "run_dir": str(resolved_run_dir) if resolved_run_dir else "",
            "run_id": _run_id(result, resolved_result_path),
        },
        "win_definition": build_win_definition(),
        "runtime_map": runtime_map,
        "lane1": lane1,
        "probe_results": probe_results,
        "win_signals": win_signals,
        "recommendations": build_recommendations(probe_results, lane1, win_signals),
    }


def build_collection_report(audits: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    status_counts: Counter[str] = Counter()
    probe_counts: dict[str, Counter[str]] = {
        spec.probe_id: Counter() for spec in BEVELIN_PROBES
    }
    aggregate: Counter[str] = Counter()
    source_refs: list[str] = []

    for audit in audits:
        source = _mapping(audit.get("source"))
        source_refs.append(_text(source.get("run_id")) or _text(source.get("result_path")))
        for result in _list(audit.get("probe_results")):
            row = _mapping(result)
            probe_id = _text(row.get("probe_id"))
            status = _text(row.get("status")) or "unknown"
            status_counts[status] += 1
            if probe_id in probe_counts:
                probe_counts[probe_id][status] += 1
        aggregate.update(_mapping(audit.get("win_signals")))

    return {
        "schema_version": BEVELIN_COLLECTION_SCHEMA_VERSION,
        "audit_count": len(audits),
        "source_refs": source_refs,
        "status_distribution": dict(sorted(status_counts.items())),
        "probe_status_distribution": {
            probe_id: dict(sorted(counter.items())) for probe_id, counter in sorted(probe_counts.items())
        },
        "aggregate_win_signals": dict(sorted(aggregate.items())),
        "audits": list(audits),
    }


def build_win_definition() -> dict[str, Any]:
    return {
        "primary": (
            "Bevelin helps Lane 1 only if it identifies specific materiality checks that current artifacts "
            "miss, keep private without explanation, or fail to convert into usable decision pressure."
        ),
        "non_goals": [
            "Do not make Lane 1 fire more often by default.",
            "Do not bulk-insert book concepts into prompts without run evidence.",
            "Do not treat private V60 consideration as public product improvement unless the output moved.",
        ],
        "local_test": [
            "Find Lane 1 findings that did not become public or private operational checks.",
            "Find silent-Lane-1 runs where V60 or other lanes already carried the Bevelin probe.",
            "Find recurring missing probes that should become subpattern or prompt candidates.",
        ],
    }


def build_runtime_map(result: Mapping[str, Any]) -> dict[str, Any]:
    audit = _mapping(result.get("audit_summary"))
    calls = [_mapping(item) for item in _list(audit.get("boundary_calls"))]
    stage_counts: Counter[str] = Counter()
    provider_counts: Counter[str] = Counter()
    model_counts: Counter[str] = Counter()
    token_usage: Counter[str] = Counter()

    for call in calls:
        stage_counts[_stage_family(_text(call.get("stage")))] += 1
        provider = _text(call.get("provider_name"))
        model = _text(call.get("model"))
        if provider:
            provider_counts[provider] += 1
        if model:
            model_counts[model] += 1
        for key in ("prompt_tokens", "completion_tokens", "total_tokens", "cached_tokens"):
            token_usage[key] += int(call.get(key) or 0)

    v60 = _mapping(result.get("v60_enrichment"))
    candidate_pool = _mapping(v60.get("candidate_pool"))
    telemetry = _mapping(v60.get("telemetry"))
    ledger = _mapping(result.get("v60_consideration_ledger"))
    coverage = _mapping(result.get("structural_coverage_card"))
    dimensions = _list(coverage.get("dimensions"))
    uncovered_dimensions = [
        item for item in (_mapping(row) for row in dimensions) if not bool(item.get("covered"))
    ]

    return {
        "llm": {
            "boundary_call_count": len(calls),
            "stage_counts": dict(sorted(stage_counts.items())),
            "provider_counts": dict(sorted(provider_counts.items())),
            "model_counts": dict(sorted(model_counts.items())),
            "token_usage": dict(sorted(token_usage.items())),
            "creates": [
                "Pass 1 tendency triage scores",
                "Pass 2 deep-check determinations",
                "Companion anchors",
                "Frame pressure cards",
                "Structural coverage classifications",
            ],
        },
        "embeddings": {
            "lane1_swiss_cheese_active": bool(audit.get("embedding_swiss_cheese_active")),
            "lane1_embedding_signal_present": bool(audit.get("embedding_signal")),
            "v60_embedding_mode": candidate_pool.get("embedding_mode"),
            "v60_embedding_affordance_candidate_count": candidate_pool.get(
                "embedding_affordance_candidate_count"
            ),
            "v60_embedding_absence_candidate_count": candidate_pool.get(
                "embedding_absence_candidate_count"
            ),
            "creates": [
                "Additional candidate tendencies for Lane 1, without removing LLM-triggered candidates",
                "Optional V60 affordance and absence candidates when V60 embedding mode is active",
            ],
        },
        "deterministic": {
            "triage_score_count": len(_list(audit.get("triage_scores"))),
            "triggered_tendency_count": len(_list(audit.get("triggered_tendencies"))),
            "deep_check_count": len(_list(audit.get("deep_check_results"))),
            "routing_decision_count": len(_list(audit.get("routing_decisions"))),
            "delta_finding_count": _delta_finding_count(result),
            "v60_selected_chunk_count": telemetry.get("selected_chunk_count"),
            "v60_ledger_transaction_count": len(_list(ledger.get("transactions"))),
            "coverage_dimension_count": len(dimensions),
            "coverage_gap_count": len(uncovered_dimensions),
            "creates": [
                "Triggered tendency set",
                "Lane 1 routes and selected model IDs",
                "DeltaCard finding surfaces",
                "V60 selection telemetry and consideration ledger",
                "Run-health and product-output hygiene checks",
            ],
        },
        "handoff": [
            "Conversation IR feeds the LLM triage/deep-check stages and deterministic route assembly.",
            "Pass 1 LLM scores plus embedding candidates decide which tendencies receive Pass 2 checks.",
            "Pass 2 detected tendencies are routed deterministically into DeltaCard pressure.",
            "Companion, frame, coverage, and V60 can still add private or public pressure when Lane 1 has no findings.",
        ],
    }


def build_lane1_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    audit = _mapping(result.get("audit_summary"))
    triage = [_mapping(item) for item in _list(audit.get("triage_scores"))]
    deep = [_mapping(item) for item in _list(audit.get("deep_check_results"))]
    detected = [item for item in deep if bool(item.get("detected"))]
    routes = [_mapping(item) for item in _list(audit.get("routing_decisions"))]
    delta_findings = _delta_findings(result)
    triggered = [_text(item) for item in _list(audit.get("triggered_tendencies")) if _text(item)]

    candidate_tendencies = [
        _text(item.get("tendency_id"))
        for item in triage
        if int(item.get("score") or 0) >= 2 and _text(item.get("tendency_id"))
    ]
    detected_tendencies = [
        _text(item.get("tendency_id")) for item in detected if _text(item.get("tendency_id"))
    ]
    routed_tendencies = [
        _text(item.get("tendency_id")) for item in routes if _text(item.get("tendency_id"))
    ]
    delta_tendencies = [
        _text(item.get("tendency_id")) for item in delta_findings if _text(item.get("tendency_id"))
    ]

    return {
        "pass1_score_count": len(triage),
        "pass1_candidate_tendency_ids": sorted(set(candidate_tendencies)),
        "triggered_tendency_count": len(triggered),
        "triggered_tendency_ids": triggered,
        "pass2_checked_count": len(deep),
        "pass2_detected_count": len(detected),
        "pass2_detected_tendency_ids": sorted(set(detected_tendencies)),
        "routed_count": len(routes),
        "routed_tendency_ids": sorted(set(routed_tendencies)),
        "delta_finding_count": len(delta_findings),
        "delta_tendency_ids": sorted(set(delta_tendencies)),
        "findings_present": bool(detected or routes or delta_findings),
    }


def build_surface_bundle(
    result: Mapping[str, Any],
    *,
    run_dir: Path | None = None,
) -> dict[str, Any]:
    public_sections = _public_sections(result, run_dir=run_dir)
    lane1_strong_sections = _lane1_strong_sections(result)
    lane1_candidate_sections = _lane1_candidate_sections(result)
    v60_used_sections = _v60_used_sections(result)
    v60_candidate_sections = _v60_candidate_sections(result)

    return {
        "public": _surface("public", public_sections),
        "lane1_strong": _surface("lane1_strong", lane1_strong_sections),
        "lane1_candidate": _surface("lane1_candidate", lane1_candidate_sections),
        "v60_used": _surface("v60_used", v60_used_sections),
        "v60_candidate": _surface("v60_candidate", v60_candidate_sections),
    }


def evaluate_probe(
    spec: ProbeSpec,
    result: Mapping[str, Any],
    *,
    surfaces: Mapping[str, Any],
    lane1_summary: Mapping[str, Any],
) -> dict[str, Any]:
    selected_models = _selected_v60_models(result)
    selected_effects = _selected_v60_effect_types(result)
    used_ledger = _used_v60_ledger_transactions(result)
    public_hits = _surface_hits(spec, _mapping(surfaces.get("public")))
    lane1_hits = _surface_hits(spec, _mapping(surfaces.get("lane1_strong")))
    lane1_candidate_hits = _surface_hits(spec, _mapping(surfaces.get("lane1_candidate")))
    v60_used_hits = _surface_hits(spec, _mapping(surfaces.get("v60_used")))
    v60_candidate_hits = _surface_hits(spec, _mapping(surfaces.get("v60_candidate")))

    model_hits = sorted(set(spec.model_ids).intersection(selected_models))
    effect_hits = sorted(set(spec.effect_types).intersection(selected_effects))
    tendency_hits = _lane1_tendency_hits(spec, lane1_summary)
    v60_used_hit = bool(v60_used_hits["material_hit"] or model_hits)
    v60_visible_claimed = any(
        _text(item.get("visible_effect"))
        for item in used_ledger
        if _text(item.get("model_id")) in spec.model_ids
    )

    status = _probe_status(
        public_hit=bool(public_hits["material_hit"]),
        lane1_hit=bool(lane1_hits["material_hit"] or tendency_hits["detected_or_routed"]),
        lane1_candidate_hit=bool(
            lane1_candidate_hits["material_hit"] or tendency_hits["candidate_or_triggered"]
        ),
        v60_used_hit=v60_used_hit,
        v60_candidate_hit=bool(v60_candidate_hits["material_hit"]),
    )

    return {
        "probe_id": spec.probe_id,
        "label": spec.label,
        "helps_with": spec.helps_with,
        "win_condition": spec.win_condition,
        "status": status,
        "public": public_hits,
        "lane1": {
            **lane1_hits,
            "candidate_hits": lane1_candidate_hits,
            "tendency_hits": tendency_hits,
        },
        "v60": {
            **v60_used_hits,
            "candidate_hits": v60_candidate_hits,
            "selected_model_hits": model_hits,
            "selected_effect_type_hits": effect_hits,
            "visible_effect_claimed": v60_visible_claimed,
        },
    }


def build_win_signals(
    probe_results: Sequence[Mapping[str, Any]],
    lane1_summary: Mapping[str, Any],
) -> dict[str, int]:
    statuses = Counter(_text(_mapping(row).get("status")) for row in probe_results)
    lane1_operationalized = 0
    lane1_unconverted = 0
    silent_supported = 0
    candidate_only = 0
    missing = 0

    for row in (_mapping(item) for item in probe_results):
        status = _text(row.get("status"))
        lane1 = _mapping(row.get("lane1"))
        tendency_hits = _mapping(lane1.get("tendency_hits"))
        lane1_hit = bool(lane1.get("matched_terms") or tendency_hits.get("detected_or_routed"))
        lane1_candidate = bool(
            _mapping(lane1.get("candidate_hits")).get("matched_terms")
            or tendency_hits.get("candidate_or_triggered")
        )
        public_hit = bool(_mapping(row.get("public")).get("material_hit"))
        v60 = _mapping(row.get("v60"))
        v60_hit = bool(
            v60.get("material_hit")
            or v60.get("selected_model_hits")
        )

        if lane1_hit and status in {"publicly_treated", "privately_considered"}:
            lane1_operationalized += 1
        if lane1_hit and status == "lane1_pressure_only":
            lane1_unconverted += 1
        if not bool(lane1_summary.get("findings_present")) and (public_hit or v60_hit):
            silent_supported += 1
        if lane1_candidate and status == "candidate_only":
            candidate_only += 1
        if status == "missing":
            missing += 1

    return {
        "publicly_treated_probe_count": statuses["publicly_treated"],
        "privately_considered_probe_count": statuses["privately_considered"],
        "lane1_pressure_only_probe_count": statuses["lane1_pressure_only"],
        "candidate_only_probe_count": statuses["candidate_only"],
        "missing_probe_count": missing,
        "lane1_operationalized_probe_count": lane1_operationalized,
        "lane1_unconverted_probe_count": lane1_unconverted,
        "silent_lane1_supported_by_other_lanes_probe_count": silent_supported,
        "lane1_candidate_only_probe_count": candidate_only,
    }


def build_recommendations(
    probe_results: Sequence[Mapping[str, Any]],
    lane1_summary: Mapping[str, Any],
    win_signals: Mapping[str, Any],
) -> list[str]:
    recommendations: list[str] = []
    if int(win_signals.get("lane1_unconverted_probe_count") or 0) > 0:
        recommendations.append(
            "Inspect Lane 1 routes whose Bevelin probe stayed internal; these are candidates for DeltaCard "
            "wording or product-surface conversion, not necessarily new detection logic."
        )
    if int(win_signals.get("silent_lane1_supported_by_other_lanes_probe_count") or 0) > 0:
        recommendations.append(
            "Treat silent Lane 1 plus active V60/public probes as a positive interaction signal; do not force "
            "Lane 1 to fire just because another lane carried the check."
        )
    missing_labels = [
        _text(row.get("label"))
        for row in (_mapping(item) for item in probe_results)
        if _text(row.get("status")) == "missing"
    ][:3]
    if missing_labels:
        recommendations.append(
            "Review recurring missing probes across more archived runs before changing prompts: "
            + ", ".join(missing_labels)
            + "."
        )
    if int(lane1_summary.get("pass2_checked_count") or 0) and not bool(lane1_summary.get("findings_present")):
        recommendations.append(
            "This run can be used as a non-firing control case: evaluate whether Bevelin improves non-finding "
            "explanations and private enrichment instead of increasing findings."
        )
    if not recommendations:
        recommendations.append(
            "No immediate Lane 1 change is indicated by this single run; compare several runs and look for "
            "repeated probe statuses before promoting anything."
        )
    return recommendations


def render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)


def render_markdown(payload: Mapping[str, Any]) -> str:
    schema = _text(payload.get("schema_version"))
    if schema == BEVELIN_COLLECTION_SCHEMA_VERSION:
        return _render_collection_markdown(payload)
    return _render_single_markdown(payload)


def _render_single_markdown(audit: Mapping[str, Any]) -> str:
    source = _mapping(audit.get("source"))
    lane1 = _mapping(audit.get("lane1"))
    runtime = _mapping(audit.get("runtime_map"))
    win = _mapping(audit.get("win_signals"))

    lines = [
        "# Bevelin Lane 1 Audit",
        "",
        f"- Run: `{_text(source.get('run_id')) or _text(source.get('result_path'))}`",
        f"- Lane 1 findings present: `{bool(lane1.get('findings_present'))}`",
        f"- Pass 1 triggered: `{lane1.get('triggered_tendency_count', 0)}`",
        f"- Pass 2 detected: `{lane1.get('pass2_detected_count', 0)}`",
        "",
        "## What Good Looks Like",
        "",
        _text(_mapping(audit.get("win_definition")).get("primary")),
        "",
        "## Runtime Map",
        "",
        "```json",
        json.dumps(
            {
                "llm": _mapping(runtime.get("llm")),
                "embeddings": _mapping(runtime.get("embeddings")),
                "deterministic": _mapping(runtime.get("deterministic")),
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "```",
        "",
        "## Win Signals",
        "",
        "```json",
        json.dumps(win, indent=2, ensure_ascii=False, sort_keys=True),
        "```",
        "",
        "## Probe Results",
        "",
    ]

    for row in (_mapping(item) for item in _list(audit.get("probe_results"))):
        lines.append(
            f"- `{row.get('probe_id')}`: **{row.get('status')}** - {row.get('label')}"
        )
        public_terms = _list(_mapping(row.get("public")).get("matched_terms"))
        v60 = _mapping(row.get("v60"))
        model_hits = _list(v60.get("selected_model_hits"))
        effect_hits = _list(v60.get("selected_effect_type_hits"))
        details = []
        if public_terms:
            details.append("public terms: " + ", ".join(str(item) for item in public_terms[:4]))
        if model_hits:
            details.append("V60 models: " + ", ".join(str(item) for item in model_hits[:4]))
        if effect_hits:
            details.append("V60 effects: " + ", ".join(str(item) for item in effect_hits[:4]))
        if details:
            lines.append("  - " + "; ".join(details))

    lines.extend(["", "## Recommendations", ""])
    for item in _list(audit.get("recommendations")):
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def _render_collection_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Bevelin Lane 1 Audit Collection",
        "",
        f"- Audit count: `{report.get('audit_count', 0)}`",
        "",
        "## Aggregate Win Signals",
        "",
        "```json",
        json.dumps(
            _mapping(report.get("aggregate_win_signals")),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "```",
        "",
        "## Status Distribution",
        "",
        "```json",
        json.dumps(
            _mapping(report.get("status_distribution")),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "```",
        "",
        "## Probe Status Distribution",
        "",
        "```json",
        json.dumps(
            _mapping(report.get("probe_status_distribution")),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        "```",
        "",
        "## Runs",
        "",
    ]
    for audit in (_mapping(item) for item in _list(report.get("audits"))):
        source = _mapping(audit.get("source"))
        win = _mapping(audit.get("win_signals"))
        lines.append(
            f"- `{_text(source.get('run_id')) or _text(source.get('result_path'))}`: "
            f"public={win.get('publicly_treated_probe_count', 0)}, "
            f"private={win.get('privately_considered_probe_count', 0)}, "
            f"missing={win.get('missing_probe_count', 0)}"
        )
    lines.append("")
    return "\n".join(lines)


def _resolve_run_dir(result_path: Path | None, run_dir: Path | str | None) -> Path | None:
    if run_dir is not None:
        return Path(run_dir)
    if result_path is not None and result_path.name == "result.json":
        return result_path.parent
    return None


def _run_id(result: Mapping[str, Any], result_path: Path | None) -> str:
    usage = _mapping(result.get("usage_summary"))
    for value in (
        result.get("run_id"),
        usage.get("run_id"),
        _mapping(result.get("audit_seed")).get("case_id"),
    ):
        text = _text(value)
        if text:
            return text
    if result_path is not None and result_path.name == "result.json":
        return "/".join(result_path.parts[-3:-1])
    return ""


def _stage_family(stage: str) -> str:
    if stage.startswith("pass1"):
        return "pass1"
    if stage.startswith("pass2"):
        return "pass2"
    if stage.startswith("companion"):
        return "companion"
    if stage.startswith("frame"):
        return "frame_pressure"
    if stage.startswith("structural_coverage"):
        return "structural_coverage"
    if stage.startswith("live_memo"):
        return "live_memo"
    return stage or "unknown"


def _public_sections(result: Mapping[str, Any], *, run_dir: Path | None) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    if run_dir is not None:
        for filename, label in (
            ("revised.txt", "Revised answer file"),
            ("memo.md", "Memo file"),
            ("gapcheck.txt", "Gap check file"),
        ):
            path = run_dir / filename
            if path.exists():
                text = path.read_text(encoding="utf-8").strip()
                if text:
                    sections.append((label, text))
    for key, label in (
        ("revised_answer", "Revised answer"),
        ("memo_pressure_check", "Memo pressure check"),
        ("memo_what_changed", "Memo what changed"),
        ("memo_take_back_or_set_aside", "Memo take-back/set-aside"),
        ("memo_orientation_note", "Memo orientation note"),
        ("memo_what_still_holds", "Memo what still holds"),
        ("gap_check_summary", "Gap check summary"),
    ):
        text = _text(result.get(key))
        if text:
            sections.append((label, text))
    return sections


def _lane1_strong_sections(result: Mapping[str, Any]) -> list[tuple[str, str]]:
    audit = _mapping(result.get("audit_summary"))
    sections: list[tuple[str, str]] = []
    for item in (_mapping(row) for row in _list(audit.get("deep_check_results"))):
        if not bool(item.get("detected")):
            continue
        sections.append(
            (
                "Pass 2 detected",
                " ".join(
                    _text(item.get(key))
                    for key in (
                        "tendency_id",
                        "tendency_name",
                        "evidence",
                        "sub_pattern",
                        "specific_passage",
                        "severity",
                        "reason",
                    )
                    if _text(item.get(key))
                ),
            )
        )
    for item in (_mapping(row) for row in _list(audit.get("routing_decisions"))):
        sections.append(("Lane 1 route", _flatten_text(item)))
    for item in _delta_findings(result):
        sections.append(("DeltaCard finding", _flatten_text(item)))
    return sections


def _lane1_candidate_sections(result: Mapping[str, Any]) -> list[tuple[str, str]]:
    audit = _mapping(result.get("audit_summary"))
    sections: list[tuple[str, str]] = []
    for tendency_id in _list(audit.get("triggered_tendencies")):
        text = _text(tendency_id)
        if text:
            sections.append(("Triggered tendency", text))
    for item in (_mapping(row) for row in _list(audit.get("triage_scores"))):
        if int(item.get("score") or 0) >= 2:
            sections.append(("Pass 1 candidate", _flatten_text(item)))
    for item in (_mapping(row) for row in _list(audit.get("deep_check_results"))):
        if not bool(item.get("detected")):
            sections.append(("Pass 2 non-finding rationale", _flatten_text(item)))
    return sections


def _v60_used_sections(result: Mapping[str, Any]) -> list[tuple[str, str]]:
    v60 = _mapping(result.get("v60_enrichment"))
    telemetry = _mapping(v60.get("telemetry"))
    sections: list[tuple[str, str]] = []
    if telemetry:
        sections.append(("V60 telemetry", _flatten_text(telemetry)))
    for item in _list(v60.get("selected_cards")):
        sections.append(("V60 selected card", _flatten_text(item)))
    for item in _used_v60_ledger_transactions(result):
        sections.append(("V60 used ledger transaction", _flatten_text(item)))
    return sections


def _v60_candidate_sections(result: Mapping[str, Any]) -> list[tuple[str, str]]:
    v60 = _mapping(result.get("v60_enrichment"))
    sections: list[tuple[str, str]] = []
    for key in ("candidate_pool", "selection_policy"):
        value = v60.get(key)
        if value:
            sections.append((f"V60 {key}", _flatten_text(value)))
    ledger = _mapping(result.get("v60_consideration_ledger"))
    for item in _list(ledger.get("transactions")):
        tx = _mapping(item)
        if _text(tx.get("disposition")) != "used":
            sections.append(("V60 non-used ledger transaction", _flatten_text(tx)))
    return sections


def _surface(label: str, sections: Sequence[tuple[str, str]]) -> dict[str, Any]:
    return {
        "label": label,
        "section_count": len(sections),
        "sections": [
            {"label": section_label, "text": text}
            for section_label, text in sections
            if text.strip()
        ],
        "text": "\n\n".join(f"{section_label}:\n{text}" for section_label, text in sections),
    }


def _surface_hits(spec: ProbeSpec, surface: Mapping[str, Any]) -> dict[str, Any]:
    text = _text(surface.get("text"))
    terms = _matched_terms(text, spec.terms)
    snippets = _snippets_for_terms(text, terms)
    return {
        "matched_terms": terms,
        "material_hit": _material_text_hit(spec, terms),
        "snippets": snippets,
    }


def _material_text_hit(spec: ProbeSpec, matched_terms: Sequence[str]) -> bool:
    normalized = {_normalize_for_match(term) for term in matched_terms}
    strong_single_terms = {_normalize_for_match(term) for term in spec.single_term_hits}
    if normalized.intersection(strong_single_terms):
        return True
    if any(" " in term or "/" in term for term in normalized):
        return True
    return len(normalized) >= 2


def _matched_terms(text: str, terms: Sequence[str]) -> list[str]:
    haystack = _normalize_for_match(text)
    matched: list[str] = []
    for term in terms:
        needle = _normalize_for_match(term)
        if not needle:
            continue
        pattern = r"(?<![a-z0-9])" + re.escape(needle) + r"(?![a-z0-9])"
        if re.search(pattern, haystack):
            matched.append(term)
    return matched


def _snippets_for_terms(text: str, terms: Sequence[str], *, limit: int = 3) -> list[str]:
    normalized = _normalize_for_match(text)
    snippets: list[str] = []
    for term in terms:
        needle = _normalize_for_match(term)
        idx = normalized.find(needle)
        if idx < 0:
            continue
        start = max(0, idx - 90)
        end = min(len(text), idx + len(term) + 90)
        snippet = " ".join(text[start:end].split())
        if snippet and snippet not in snippets:
            snippets.append(snippet)
        if len(snippets) >= limit:
            break
    return snippets


def _normalize_for_match(text: str) -> str:
    lowered = str(text or "").lower()
    lowered = re.sub(r"[_-]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered)


def _probe_status(
    *,
    public_hit: bool,
    lane1_hit: bool,
    lane1_candidate_hit: bool,
    v60_used_hit: bool,
    v60_candidate_hit: bool,
) -> str:
    if public_hit:
        return "publicly_treated"
    if v60_used_hit:
        return "privately_considered"
    if lane1_hit:
        return "lane1_pressure_only"
    if lane1_candidate_hit or v60_candidate_hit:
        return "candidate_only"
    return "missing"


def _lane1_tendency_hits(spec: ProbeSpec, lane1_summary: Mapping[str, Any]) -> dict[str, Any]:
    detected_or_routed = sorted(
        set(spec.related_tendencies).intersection(
            set(_list(lane1_summary.get("pass2_detected_tendency_ids")))
            | set(_list(lane1_summary.get("routed_tendency_ids")))
            | set(_list(lane1_summary.get("delta_tendency_ids")))
        )
    )
    candidate_or_triggered = sorted(
        set(spec.related_tendencies).intersection(
            set(_list(lane1_summary.get("pass1_candidate_tendency_ids")))
            | set(_list(lane1_summary.get("triggered_tendency_ids")))
        )
    )
    return {
        "detected_or_routed": detected_or_routed,
        "candidate_or_triggered": candidate_or_triggered,
    }


def _selected_v60_models(result: Mapping[str, Any]) -> set[str]:
    v60 = _mapping(result.get("v60_enrichment"))
    telemetry = _mapping(v60.get("telemetry"))
    models = {_text(item) for item in _list(telemetry.get("selected_model_ids")) if _text(item)}
    for tx in _used_v60_ledger_transactions(result):
        model_id = _text(tx.get("model_id"))
        if model_id:
            models.add(model_id)
    return models


def _selected_v60_effect_types(result: Mapping[str, Any]) -> set[str]:
    v60 = _mapping(result.get("v60_enrichment"))
    telemetry = _mapping(v60.get("telemetry"))
    effects = set()
    for effect in _mapping(telemetry.get("selected_chunk_effect_types")):
        if _text(effect):
            effects.add(_text(effect))
    return effects


def _used_v60_ledger_transactions(result: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    ledger = _mapping(result.get("v60_consideration_ledger"))
    return [
        _mapping(item)
        for item in _list(ledger.get("transactions"))
        if _text(_mapping(item).get("disposition")) == "used"
    ]


def _delta_findings(result: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    delta = _mapping(result.get("delta_card"))
    findings = _list(delta.get("findings"))
    if not findings:
        findings = [*_list(delta.get("top_findings")), *_list(delta.get("secondary_findings"))]
    return [_mapping(item) for item in findings]


def _delta_finding_count(result: Mapping[str, Any]) -> int:
    return len(_delta_findings(result))


def _flatten_text(value: Any) -> str:
    parts: list[str] = []

    def visit(item: Any) -> None:
        if isinstance(item, Mapping):
            for key, nested in item.items():
                if key in {"raw_message_content", "prompt", "messages"}:
                    continue
                parts.append(str(key))
                visit(nested)
        elif isinstance(item, list | tuple):
            for nested in item:
                visit(nested)
        elif item is not None:
            text = str(item).strip()
            if text:
                parts.append(text)

    visit(value)
    return " ".join(parts)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value or "").strip()
