from __future__ import annotations

from pathlib import Path

from engine.system_b.reasoning_substrate_coverage import (
    build_enrichment_coverage_audit,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_full_corpus_audit_reports_runtime_v4_and_source_custody_counts() -> None:
    audit = build_enrichment_coverage_audit(REPO_ROOT)

    assert audit["runtime_model_count"] == 222
    assert audit["v4_reviewed_model_count"] == 55
    assert audit["graph_only_runtime_model_count"] == 167
    assert audit["v4_model_ids_outside_runtime_graph"] == []
    assert audit["source_custody_model_count"] == 222
    assert audit["runtime_model_ids_missing_source_custody_count"] == 0
    assert audit["runtime_model_ids_missing_source_custody"] == []
    assert "chain-of-verification" in audit["runtime_model_ids_missing_v4"]
    assert "reviewed_source_custody_model_count" not in audit
    assert "runtime_model_ids_missing_reviewed_source_custody" not in audit


def test_full_corpus_audit_reports_runtime_graph_field_and_reasoning_type_gaps() -> None:
    audit = build_enrichment_coverage_audit(REPO_ROOT)

    graph_fields = audit["runtime_graph_field_coverage"]
    assert graph_fields["select_when"]["models_with_field"] == 222
    assert graph_fields["danger_when"]["models_with_field"] == 222
    assert graph_fields["failure_modes"]["models_with_field"] == 222
    assert graph_fields["premortem_questions"]["models_with_field"] == 222
    assert graph_fields["heuristics"]["models_with_field"] == 222
    assert graph_fields["reasoning_types"]["models_with_field"] == 222

    reasoning_gaps = audit["reasoning_type_coverage_gaps"]
    assert reasoning_gaps["diagnostic"]["runtime_model_count"] == 102
    assert reasoning_gaps["diagnostic"]["v4_reviewed_model_count"] == 19
    assert reasoning_gaps["diagnostic"]["graph_only_model_count"] == 83
    assert reasoning_gaps["systems"]["graph_only_model_count"] == 62


def test_full_corpus_audit_prioritizes_graph_only_models_with_static_lane_signals() -> None:
    audit = build_enrichment_coverage_audit(REPO_ROOT)

    priorities = {
        row["model_id"]: row
        for row in audit["static_lane_signal_graph_only_priorities"]
    }
    assert priorities["game-theory-payoffs"]["static_lane_signal_count"] >= 5
    assert priorities["confirmation-bias"]["static_lane_signal_sources"][
        "lane3_reframing_route"
    ] == 4

    first_batch = audit["recommended_expansion_batches"][0]
    assert first_batch["batch_size"] <= 30
    assert set(first_batch["model_ids"]).issubset(
        set(audit["runtime_model_ids_missing_v4"])
    )
