from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_JSON = (
    REPO_ROOT
    / "docs/conversation-understanding/hybrid-reasoning-boundary-v0.json"
)
BOUNDARY_MD = (
    REPO_ROOT
    / "docs/conversation-understanding/hybrid-reasoning-boundary-v0.md"
)
V01_PLAN = REPO_ROOT / "plans/lolla-semantic-kernel-v0.1-plan-2026-07-10.md"
LINKED_ACTIVE_DOCS = [
    REPO_ROOT / "plans/lolla-core-reasoning-audit-assessment-and-prd-2026-07-09.md",
    REPO_ROOT / "plans/lolla-product-blueprint-and-repository-gardening-2026-07-09.md",
    REPO_ROOT / "docs/conversation-understanding/reasoning-pattern-packet-v0.md",
    REPO_ROOT / "research/core-semantic-corpus-2026-07-09/core-semantic-corpus-result.md",
]


def test_hybrid_boundary_assigns_semantics_and_structure_to_different_authorities() -> None:
    payload = json.loads(BOUNDARY_JSON.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "lolla.hybrid_reasoning_boundary.v0"
    assert payload["status"] == "binding_for_new_core_work"
    assert payload["authorities"] == {
        "semantic": "llm_or_human",
        "structural": "deterministic_harness",
        "final_decision": "user_or_designated_reasoning_agent",
    }

    allowed = set(payload["deterministic_allowed"])
    forbidden = set(payload["deterministic_forbidden"])
    assert {
        "validate_exact_quotes_and_offsets",
        "traverse_declared_graph_for_candidate_recall",
        "lint_fact_leakage_and_privacy",
        "assemble_lineage_receipts_and_evaluation_metrics",
    } <= allowed
    assert {
        "assign_current_question_from_surface_rules",
        "infer_user_mind_change",
        "infer_semantic_events_from_keywords",
        "assign_stance_relation_from_surface_rules",
        "decide_thread_under_carry_from_surface_rules",
        "treat_evaluation_thresholds_as_semantic_truth",
    } <= forbidden
    assert allowed.isdisjoint(forbidden)

    properties = payload["required_properties"]
    assert properties["authoritative_source_preserved"] is True
    assert properties["ambiguity_preserved"] is True
    assert properties["derivations_preserve_component_evidence"] is True
    assert properties["graph_receives_fact_free_projection_only"] is True
    assert properties["graph_recall_is_not_applicability_judgment"] is True
    assert properties["audit_is_not_verification"] is True
    assert properties["process_completeness_is_not_decision_approval"] is True
    assert properties["runtime_graph_modified_by_this_contract"] is False


def test_boundary_flow_keeps_graph_recall_separate_from_applicability() -> None:
    payload = json.loads(BOUNDARY_JSON.read_text(encoding="utf-8"))
    stages = {item["stage"]: item for item in payload["boundary_flow"]}
    assert stages["semantic_proposals"]["owner"] == "llm"
    assert stages["evidence_validation"]["owner"] == "deterministic_harness"
    assert stages["graph_candidate_recall"] == {
        "stage": "graph_candidate_recall",
        "owner": "deterministic_harness",
        "job": "reproducible_candidate_expansion",
    }
    assert stages["applicability_and_pressure"] == {
        "stage": "applicability_and_pressure",
        "owner": "llm",
        "job": "semantic_judgment",
    }


def test_v01_plan_does_not_reintroduce_deterministic_semantic_gates() -> None:
    boundary = BOUNDARY_MD.read_text(encoding="utf-8")
    plan = V01_PLAN.read_text(encoding="utf-8")
    assert "The deterministic middle is a courier, validator, and accountant" in boundary
    assert "Begin with SK1 only" in plan
    assert "deterministically select the current question" in plan
    assert "will not" in plan
    assert "Deterministic reconciliation may join identical IDs" in plan
    assert "It may not decide which interpretation is semantically best." in plan
    assert "no regex, keyword, or case-type semantic inference is introduced" in plan
    assert "Graph integration is not an exit option from this plan." in plan


def test_active_core_docs_link_to_the_binding_boundary() -> None:
    boundary_ref = "hybrid-reasoning-boundary-v0.md"
    for path in LINKED_ACTIVE_DOCS:
        assert boundary_ref in path.read_text(encoding="utf-8"), path

    payload = json.loads(BOUNDARY_JSON.read_text(encoding="utf-8"))
    for source in payload["source_lineage"]:
        if source.startswith("https://"):
            continue
        assert (REPO_ROOT / source).is_file(), source
