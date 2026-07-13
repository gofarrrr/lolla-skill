#!/usr/bin/env python3
"""Build a review-safe C0-C8 bridge from an existing local Lolla run.

The builder reads local/private artifacts but emits only structural summaries,
hashes, counts, review labels, and explicit non-claims. It never copies source
conversation, revised-answer, memo, provider, or private-ledger text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = "lolla.end_to_end_evidence_bridge.v0"
REQUIRED_ARCHIVE_FILES = (
    "conversation.txt",
    "extraction.json",
    "result.json",
    "revised.txt",
    "memo.md",
    "agent_result.json",
    "evaluation.json",
    "reasoning_trace.json",
    "graph_survival_report.json",
    "extraction_adequacy_report.json",
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_inventory(archive: Path) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for filename in REQUIRED_ARCHIVE_FILES:
        path = archive / filename
        inventory.append(
            {
                "artifact": filename,
                "present": path.is_file(),
                "bytes": path.stat().st_size if path.is_file() else 0,
                "sha256": f"sha256:{_sha256(path)}" if path.is_file() else "",
            }
        )
    return inventory


def _find_case(items: Iterable[Any], case_id: str) -> dict[str, Any]:
    for item in items:
        if isinstance(item, dict) and item.get("case_id") == case_id:
            return item
    raise ValueError(f"case not found: {case_id}")


def _semantic_metric(
    runs: list[Mapping[str, Any]],
    *,
    field: str,
    observation_ids: set[str],
) -> dict[str, Any]:
    per_run = [set(map(str, run.get(field, []))) for run in runs]
    stable = set.intersection(*per_run) if per_run else set()
    ever = set.union(*per_run) if per_run else set()
    opportunities = len(observation_ids) * len(per_run)
    recovered = sum(len(values & observation_ids) for values in per_run)
    return {
        "weighted_recall": recovered / opportunities if opportunities else 0.0,
        "stable_observation_count": len(stable & observation_ids),
        "ever_observation_count": len(ever & observation_ids),
        "never_observation_count": len(observation_ids - ever),
        "observation_count": len(observation_ids),
        "run_count": len(per_run),
    }


def _semantic_summary(result: Mapping[str, Any], case_id: str) -> dict[str, Any]:
    case = _find_case(result.get("per_case", []), case_id)
    runs = [item for item in case.get("runs", []) if isinstance(item, dict)]
    observation_ids: set[str] = set()
    for run in runs:
        observation_ids.update(map(str, run.get("evidence_matches", {}).keys()))
    return {
        "case_id": case_id,
        "contract_status": result.get("contract_status"),
        "reviewed_observation_count": len(observation_ids),
        "reasoning_concept_anywhere": _semantic_metric(
            runs,
            field="concept_anywhere_observation_ids",
            observation_ids=observation_ids,
        ),
        "reasoning_concept_acceptable_role": _semantic_metric(
            runs,
            field="concept_acceptable_role_observation_ids",
            observation_ids=observation_ids,
        ),
        "audit_first_introduction": _semantic_metric(
            runs,
            field="first_introduction_observation_ids",
            observation_ids=observation_ids,
        ),
        "audit_temporal_complete": _semantic_metric(
            runs,
            field="audit_complete_observation_ids",
            observation_ids=observation_ids,
        ),
    }


def _human_review_summary(
    review: Mapping[str, Any],
    *,
    case_id: str,
    relation: str,
) -> dict[str, Any]:
    case = _find_case(review.get("cases", []), case_id)
    human = case.get("human_review", {})
    return {
        "evidence_relation": relation,
        "case_id": case_id,
        "run_id": case.get("run_id"),
        "review_status": human.get("review_status"),
        "useful_friction": human.get("useful_friction"),
        "noisy_friction": human.get("noisy_friction"),
        "missing_friction": human.get("missing_friction"),
        "revised_answer_improved": human.get("revised_answer_improved"),
        "safe_for_agent_use": human.get("safe_for_agent_use"),
        "action_changing_delta": case.get("action_changing_delta"),
        "artifact_sufficiency": case.get("artifact_sufficiency"),
    }


def build_bridge(
    *,
    archive: Path,
    semantic_result_path: Path,
    semantic_case_id: str,
    human_review_path: Path,
    human_review_case_id: str,
    review_relation: str,
) -> dict[str, Any]:
    if review_relation not in {"exact_run", "analogous_case_not_exact_run"}:
        raise ValueError(f"unsupported review relation: {review_relation}")
    missing = [name for name in REQUIRED_ARCHIVE_FILES if not (archive / name).is_file()]
    if missing:
        raise ValueError(f"archive missing required files: {missing}")

    agent = _load_json(archive / "agent_result.json")
    evaluation = _load_json(archive / "evaluation.json")
    adequacy = _load_json(archive / "extraction_adequacy_report.json")
    graph = _load_json(archive / "graph_survival_report.json")
    trace = _load_json(archive / "reasoning_trace.json")
    semantic = _semantic_summary(_load_json(semantic_result_path), semantic_case_id)
    human_review = _human_review_summary(
        _load_json(human_review_path),
        case_id=human_review_case_id,
        relation=review_relation,
    )

    graph_summary = graph.get("summary", {})
    process = trace.get("process", {})
    usage = process.get("usage", {})
    trace_adequacy = trace.get("trace_adequacy", {})
    capture = agent.get("capture_adequacy", {})
    provenance = adequacy.get("provenance_gap_findings", {})

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "review_safe_structural_bridge",
        "review_mode": "local_private_read_only_safe_summary",
        "raw_private_content_included": False,
        "local_absolute_paths_included": False,
        "archive_mutated": False,
        "builder_model_calls": 0,
        "source_run": {
            "case_id": agent.get("case_id"),
            "run_id": agent.get("run_id"),
            "status": agent.get("status"),
            "run_health_overall": agent.get("run_health_overall"),
            "product_output_health": agent.get("product_output_health"),
            "live_output_health": agent.get("live_output_health"),
            "caller_action": agent.get("caller_action"),
            "risk_mode": agent.get("risk_mode"),
            "artifact_inventory": _artifact_inventory(archive),
        },
        "capabilities": {
            "c0_capture_and_custody": {
                "capture_status": capture.get("status"),
                "declared_turn_count": capture.get("declared_turn_count"),
                "captured_turn_count": capture.get("captured_turn_count"),
                "omitted_turn_count": capture.get("omitted_turn_count"),
                "evaluation_summary": evaluation.get("summary"),
                "quote_fabrication_count": provenance.get("quote_fabrication_count"),
                "fields_with_no_source_grounding": provenance.get(
                    "fields_with_no_source_grounding", []
                ),
                "fields_only_turn_ref_grounded": provenance.get(
                    "fields_only_turn_ref_grounded", []
                ),
            },
            "c1_c3_semantic_and_temporal": semantic,
            "c4_c5_pressure_and_graph": {
                "raw_lane_signal_count": graph_summary.get("raw_lane_signal_count"),
                "lane_candidate_count": graph_summary.get("lane_candidate_count"),
                "selected_card_count": graph_summary.get("selected_card_count"),
                "selected_chunk_count": graph_summary.get("selected_chunk_count"),
                "selected_model_ids": graph_summary.get("selected_model_ids", []),
                "suppressed_signal_count": graph_summary.get("suppressed_signal_count"),
                "budget_suppressed_signal_count": graph_summary.get(
                    "budget_suppressed_signal_count"
                ),
                "unadjudicated_candidate_count": graph_summary.get(
                    "unadjudicated_candidate_count"
                ),
                "private_table_item_count": graph_summary.get("private_table_item_count"),
                "private_table_disposition_counts": graph_summary.get(
                    "private_table_disposition_counts", {}
                ),
                "v60_transaction_count": graph_summary.get("v60_transaction_count"),
                "v60_disposition_counts": graph_summary.get(
                    "v60_disposition_counts", {}
                ),
            },
            "c6_reconsideration_utility": human_review,
            "c7_receipt_and_transfer": {
                "trace_status": trace_adequacy.get("status"),
                "future_review_ready": trace_adequacy.get("future_review_ready"),
                "error_analysis_ready": trace_adequacy.get("error_analysis_ready"),
                "coverage": trace_adequacy.get("coverage", {}),
                "missing_context": trace_adequacy.get("missing_context", []),
                "user_usefulness_review_status": trace.get(
                    "user_usefulness_review", {}
                ).get("status"),
                "outcome_review_status": trace.get("outcome_review_state", {}).get(
                    "status"
                ),
            },
            "c8_operability": {
                "estimated_total_cost_usd": agent.get("usage", {}).get(
                    "estimated_total_cost_usd"
                ),
                "vendor_calls": usage.get("vendor_calls", {}),
                "total_vendor_call_count": usage.get("total_vendor_call_count"),
                "cost_estimate_state": agent.get("usage", {}).get(
                    "cost_estimate_state"
                ),
            },
        },
        "decision": {
            "supports": [
                "existing_run_can_be_traced_across_capture_semantics_pressure_revision_and_receipt",
                "current_packet_has_material_concept_coverage_but_incomplete_stability_and_placement",
                "existing_human_review_supports_product_delta_on_an_analogous_case",
            ],
            "does_not_support": [
                "semantic_kernel_integration_improves_reconsideration",
                "lolla_beats_a_strong_fresh_reconsideration_control",
                "receipt_completeness_proves_reasoning_quality",
                "selected_or_used_pressure_items_were_all_causally_necessary",
            ],
            "next_gate": "strong_control_downstream_ablation_after_no_cost_trace_review",
        },
        "non_claims": [
            "not_a_quality_score",
            "not_a_human_review_of_the_source_run_unless_relation_is_exact_run",
            "not_causal_attribution",
            "not_product_proof",
            "not_agent_approval",
            "not_runtime_integration_authority",
        ],
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    source = payload["source_run"]
    caps = payload["capabilities"]
    semantic = caps["c1_c3_semantic_and_temporal"]
    graph = caps["c4_c5_pressure_and_graph"]
    utility = caps["c6_reconsideration_utility"]
    receipt = caps["c7_receipt_and_transfer"]
    operations = caps["c8_operability"]

    def metric_line(name: str) -> str:
        metric = semantic[name]
        return (
            f"| `{name}` | {metric['weighted_recall']:.3f} | "
            f"{metric['stable_observation_count']} / {metric['observation_count']} |"
        )

    models = ", ".join(f"`{item}`" for item in graph["selected_model_ids"])
    return "\n".join(
        [
            "# End-to-End Evidence Bridge",
            "",
            f"Source run: `{source['case_id']}` / `{source['run_id']}`",
            "",
            "This is a read-only, review-safe bridge. It contains counts, hashes,",
            "status fields, and existing review labels, not raw conversation or",
            "private reasoning content.",
            "",
            "## C0 — Capture and custody",
            "",
            f"- Run health: `{source['run_health_overall']}`; product output: `{source['product_output_health']}`.",
            f"- Captured {caps['c0_capture_and_custody']['captured_turn_count']} / {caps['c0_capture_and_custody']['declared_turn_count']} turns.",
            f"- Live-output health remains `{source['live_output_health']}`.",
            "",
            "## C1-C3 — Semantic and temporal packet",
            "",
            "| measure | weighted recall | stable observations |",
            "| --- | ---: | ---: |",
            metric_line("reasoning_concept_anywhere"),
            metric_line("reasoning_concept_acceptable_role"),
            metric_line("audit_first_introduction"),
            metric_line("audit_temporal_complete"),
            "",
            "## C4-C5 — Pressure and graph",
            "",
            f"- {graph['raw_lane_signal_count']} raw lane signals became {graph['lane_candidate_count']} candidates, {graph['selected_card_count']} selected cards, and {graph['selected_chunk_count']} selected chunks.",
            f"- Selected models: {models}.",
            f"- {graph['suppressed_signal_count']} signals were suppressed; {graph['unadjudicated_candidate_count']} candidates were left unadjudicated.",
            "",
            "## C6 — Reconsideration utility",
            "",
            f"- Review relation: `{utility['evidence_relation']}`.",
            f"- Existing review: `{utility['review_status']}`; improved: `{utility['revised_answer_improved']}`; useful friction: `{utility['useful_friction']}`.",
            "- This supports a product-delta hypothesis, not causal credit for the new semantic kernel.",
            "",
            "## C7-C8 — Receipt and operability",
            "",
            f"- Trace: `{receipt['trace_status']}`; future-review ready: `{str(receipt['future_review_ready']).lower()}`; error-analysis ready: `{str(receipt['error_analysis_ready']).lower()}`.",
            f"- User usefulness review: `{receipt['user_usefulness_review_status']}`; outcome review: `{receipt['outcome_review_status']}`.",
            f"- Original run: {operations['total_vendor_call_count']} vendor calls; estimated cost `${operations['estimated_total_cost_usd']:.5f}`.",
            "",
            "## Decision",
            "",
            "The run is traceable and the analogous human review supports a real",
            "action-changing delta. The missing proof is whether the offline semantic",
            "kernel or Lolla pressure beats a strong fresh reconsideration control.",
            "Do not spend more extraction calls before that downstream question is frozen.",
            "",
        ]
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--semantic-result", type=Path, required=True)
    parser.add_argument("--semantic-case-id", required=True)
    parser.add_argument("--human-review", type=Path, required=True)
    parser.add_argument("--human-review-case-id", required=True)
    parser.add_argument(
        "--review-relation",
        choices=("exact_run", "analogous_case_not_exact_run"),
        required=True,
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    payload = build_bridge(
        archive=args.archive,
        semantic_result_path=args.semantic_result,
        semantic_case_id=args.semantic_case_id,
        human_review_path=args.human_review,
        human_review_case_id=args.human_review_case_id,
        review_relation=args.review_relation,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(render_markdown(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
