from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/evals/build_reasoning_pressure_handoff_shadow.py"
FIXTURE = REPO_ROOT / "tests/fixtures/core_semantic_validation/case_01_enterprise_logo_beta"
SHADOW = (
    REPO_ROOT
    / "research/core-semantic-sk3-2026-07-10/case-01-enterprise-logo-beta/shadow-01.json"
)


def _module():
    spec = importlib.util.spec_from_file_location("handoff_builder", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _graph_report(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.graph_survival_report.test.v0",
                "candidate_survival": [
                    {"model_id": "authority-bias"},
                    {"model_id": "problem-framing-and-reframing"},
                    {"model_id": "falsifiability"},
                ],
            }
        ),
        encoding="utf-8",
    )


def test_builder_seals_real_hashes_without_selecting_semantics(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    _graph_report(graph_path)
    payload, validation = _module().build_lineage_backed_handoff(
        draft_path=FIXTURE / "reasoning-pressure-handoff.example.json",
        conversation_path=FIXTURE / "conversation.txt",
        semantic_shadow_path=SHADOW,
        reasoning_pattern_packet_path=FIXTURE / "reasoning-pattern-packet.example.json",
        graph_report_path=graph_path,
    )
    assert payload["status"] == "research_candidate"
    assert payload["lineage"]["graph_version"] == (
        "lolla.graph_survival_report.test.v0"
    )
    assert payload["lineage"]["graph_trace_artifact_sha256"].startswith("sha256:")
    assert validation["status"] == "valid_for_shadow_evaluation_only"
    assert validation["draft_semantic_selection_preserved"] is True
    assert validation["builder_model_calls"] == 0
    assert validation["semantic_relevance_validated"] is False
    assert validation["runtime_integration_authorized"] is False


def test_builder_rejects_pattern_packet_not_linked_to_shadow(tmp_path: Path) -> None:
    graph_path = tmp_path / "graph.json"
    _graph_report(graph_path)
    pattern = json.loads(
        (FIXTURE / "reasoning-pattern-packet.example.json").read_text()
    )
    pattern["provenance"]["source_interpretation_sha256"] = "0" * 64
    pattern_path = tmp_path / "pattern.json"
    pattern_path.write_text(json.dumps(pattern), encoding="utf-8")
    with pytest.raises(ValueError, match="does not hash-link"):
        _module().build_lineage_backed_handoff(
            draft_path=FIXTURE / "reasoning-pressure-handoff.example.json",
            conversation_path=FIXTURE / "conversation.txt",
            semantic_shadow_path=SHADOW,
            reasoning_pattern_packet_path=pattern_path,
            graph_report_path=graph_path,
        )
