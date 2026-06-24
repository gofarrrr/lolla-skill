from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.graph_survival_report import (
    build_graph_survival_report,
    graph_survival_summary_for_trace,
    render_graph_survival_markdown,
    write_graph_survival_artifacts,
)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_graph_survival_report_preserves_used_guardrail_and_unadjudicated_signals(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_json(
        run_dir / "result.json",
        {
            "v60_enrichment": {
                "status": "active",
                "candidate_pool": {
                    "lane_candidate_count": 3,
                    "raw_lane_signal_count": 5,
                    "embedding_mode": "on",
                    "embedding_model_hits": [
                        {"model_id": "calculated-risk-taking", "score": 0.91},
                        {"model_id": "risk-vs-uncertainty", "score": 0.84},
                        {"model_id": "trade-offs", "score": 0.73},
                    ],
                    "lane_candidates": [
                        {
                            "model_id": "trade-offs",
                            "source": "lane1_delta_selected+lane1_selected",
                            "reason": "Hidden household costs are being accepted.",
                            "evidence": "The financial EV does not need to be positive.",
                        },
                        {
                            "model_id": "information-asymmetry",
                            "source": "lane2_companion_anchor",
                            "reason": "Interview-loop information is biased.",
                            "evidence": "Talk to employees outside the loop.",
                        },
                        {
                            "model_id": "risk-vs-uncertainty",
                            "source": "lane3_frame_route_candidate",
                            "reason": "temporal_fixation",
                        },
                    ],
                },
                "selected_cards": [
                    {
                        "card_id": "v60-card-001-trade-offs",
                        "model_id": "trade-offs",
                        "display_name": "Trade Offs",
                        "selection_source": "lane_preserved",
                        "selection_reason": "Lane 1 selected this model.",
                        "selected_affordance_cards": [{"chunk_id": "aff::trade-offs.household"}],
                        "selected_absence_records": [],
                    },
                    {
                        "card_id": "v60-card-002-calculated-risk-taking",
                        "model_id": "calculated-risk-taking",
                        "display_name": "Calculated Risk Taking",
                        "selection_source": "embedding_model_recall",
                        "selection_reason": "Add embedding-recalled model.",
                        "selected_affordance_cards": [
                            {"chunk_id": "aff::calculated-risk-taking.bounded-wager"}
                        ],
                        "selected_absence_records": [
                            {
                                "chunk_id": (
                                    "abs::calculated-risk-taking::calculated-label-"
                                    "with-unbounded-downside"
                                )
                            }
                        ],
                    },
                ],
                "telemetry": {
                    "selected_chunk_count": 3,
                    "selection_source_counts": {
                        "embedding_model_recall": 1,
                        "lane_preserved": 1,
                    },
                    "skipped_candidates": [
                        {
                            "model_id": "risk-vs-uncertainty",
                            "source": "embedding_fill",
                            "reason": "not_presented_packet_cap",
                            "stage": "fill",
                            "score": 0.84,
                        }
                    ],
                    "not_presented_candidate_count": 1,
                },
            }
        },
    )
    _write_json(
        run_dir / "v60_ledger.json",
        {
            "schema_version": "v60_skill_consideration_ledger.v1",
            "transactions": [
                {
                    "card_id": "v60-card-001-trade-offs",
                    "model_id": "trade-offs",
                    "chunk_id": "aff::trade-offs.household",
                    "chunk_kind": "affordance",
                    "disposition": "used",
                    "route": "updated_position",
                    "visible_effect": "Added family trade-off ledger.",
                    "private_guardrail": "",
                },
                {
                    "card_id": "v60-card-002-calculated-risk-taking",
                    "model_id": "calculated-risk-taking",
                    "chunk_id": "aff::calculated-risk-taking.bounded-wager",
                    "chunk_kind": "affordance",
                    "disposition": "used",
                    "route": "private_guardrail",
                    "visible_effect": "",
                    "private_guardrail": "Do not call the choice calculated until downside is bounded.",
                },
            ],
        },
    )
    _write_json(
        run_dir / "pre_step6_private_table_ledger.json",
        {
            "schema_version": "pre_step6_private_table_ledger.v1",
            "status": "completed",
            "items": [
                {
                    "source_id": "lane2::information-asymmetry",
                    "source_kind": "lane2_anchor",
                    "title": "Information Asymmetry",
                    "source_atom_id": "information-asymmetry",
                    "disposition": "used",
                    "why": "Shifted diligence toward stories.",
                    "visible_effect": "Startup diligence now asks for concrete episodes.",
                    "private_guardrail": "",
                }
            ],
        },
    )

    report = build_graph_survival_report(run_dir)

    assert report["schema_version"] == "lolla.graph_survival_report.v0.1"
    assert report["noise_policy"]["unselected_does_not_mean_noise"] is True
    assert report["summary"]["answer_delta_model_count"] == 2
    assert report["summary"]["private_guardrail_model_count"] == 1
    assert report["summary"]["suppressed_signal_count"] == 1
    assert report["summary"]["budget_suppressed_signal_count"] == 1
    assert report["summary"]["budget_suppressed_model_count"] == 1
    by_model = {item["model_id"]: item for item in report["candidate_survival"]}
    assert by_model["trade-offs"]["survival_state"] == "answer_delta"
    assert by_model["information-asymmetry"]["survival_state"] == "answer_delta"
    assert by_model["calculated-risk-taking"]["survival_state"] == "private_guardrail"
    assert by_model["risk-vs-uncertainty"]["survival_state"] == "suppressed_by_packet_cap"
    assert by_model["risk-vs-uncertainty"]["unknown_noise_status"] is True

    embedding_hits = report["embedding_selection"]["hits"]
    risk_hit = next(item for item in embedding_hits if item["model_id"] == "risk-vs-uncertainty")
    assert risk_hit["selected_for_v60"] is False
    assert risk_hit["unknown_noise_status"] is True

    write_graph_survival_artifacts(run_dir)
    summary = graph_survival_summary_for_trace(run_dir)
    # Direct reasoning_trace summaries must surface packet-cap suppressions;
    # otherwise the trace can say "0 unadjudicated" while hiding plausible lenses.
    assert summary["budget_suppressed_signal_count"] == 1
    assert summary["budget_suppressed_model_count"] == 1
    assert summary["top_budget_suppressed_lenses"] == [
        {
            "model_id": "risk-vs-uncertainty",
            "reason": "not_presented_packet_cap",
            "source": "embedding_fill",
            "stage": "fill",
            "score": 0.84,
            "research_status": "plausible_budget_suppressed",
            "unknown_noise_status": True,
        }
    ]

    markdown = render_graph_survival_markdown(report)
    assert "Graph Survival Report" in markdown
    assert "Unselected signals are preserved as unknown" in markdown


def test_graph_survival_report_joins_lane2_ledger_items_without_source_atom_id(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_json(
        run_dir / "result.json",
        {
            "v60_enrichment": {
                "status": "active",
                "candidate_pool": {
                    "lane_candidate_count": 1,
                    "raw_lane_signal_count": 1,
                    "embedding_mode": "off",
                    "embedding_model_hits": [],
                    "lane_candidates": [
                        {
                            "model_id": "second-order-thinking",
                            "source": "lane2_companion_anchor",
                            "reason": "The answer underweighted downstream effects.",
                            "evidence": "Month-3 and month-6 failure states were missing.",
                        }
                    ],
                },
                "selected_cards": [],
                "telemetry": {
                    "selected_chunk_count": 0,
                    "selection_source_counts": {},
                    "skipped_candidates": [],
                    "not_presented_candidate_count": 0,
                },
            }
        },
    )
    _write_json(
        run_dir / "v60_ledger.json",
        {
            "schema_version": "v60_skill_consideration_ledger.v1",
            "transactions": [],
        },
    )
    _write_json(
        run_dir / "pre_step6_private_table_ledger.json",
        {
            "schema_version": "pre_step6_private_table_ledger.v1",
            "status": "completed",
            "items": [
                {
                    "source_id": "lane2::second-order-thinking",
                    "source_kind": "lane2_anchor",
                    "title": "Second Order Thinking",
                    "disposition": "used",
                    "why": "Shifted the answer toward downstream failure states.",
                    "visible_effect": "Added month-3 and month-6 stop-loss thresholds.",
                    "private_guardrail": "Do not let first-order learning value hide second-order family load.",
                }
            ],
        },
    )

    report = build_graph_survival_report(run_dir)

    by_model = {item["model_id"]: item for item in report["candidate_survival"]}
    row = by_model["second-order-thinking"]
    assert row["pre_step6_item_count"] == 1
    assert row["pre_step6_disposition_counts"] == {"used": 1}
    assert row["survival_state"] == "answer_delta"
    assert report["summary"]["answer_delta_model_count"] == 1


def test_write_graph_survival_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_json(run_dir / "result.json", {"v60_enrichment": {"status": "disabled"}})

    json_path, md_path, report = write_graph_survival_artifacts(run_dir)

    assert json_path.name == "graph_survival_report.json"
    assert md_path.name == "graph_survival_report.md"
    assert json_path.exists()
    assert md_path.exists()
    assert report["summary"]["v60_status"] == "disabled"
