from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-data-exposure-audit-v0.md"
AUDIT = REPO_ROOT / "docs/product/observatory-data-exposure-audit-v0.json"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-data-exposure-audit-v0/review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def test_data_exposure_audit_files_exist_and_are_indexed() -> None:
    assert DOC.exists()
    assert AUDIT.exists()
    assert REVIEW.exists()

    readme = _read(README)
    assert "Observatory Data Exposure Audit" in readme
    assert "observatory-data-exposure-audit-v0.md" in readme
    assert "observatory-data-exposure-audit-v0.json" in readme


def test_data_exposure_audit_defines_visibility_layers_and_counts() -> None:
    data = _json(AUDIT)

    assert data["schema"] == "lolla.observatory_data_exposure_audit.v0"
    assert data["decision_gate"] == "proceed_to_graph_substrate_and_memory_export_design"

    expected_layers = {
        "default_workspace_summary",
        "primary_product_surface",
        "expandable_product_detail",
        "optional_technical_inspection",
        "agent_memory_export",
        "future_or_suggestion_only",
        "internal_only",
        "private_hidden",
    }
    assert set(data["layer_vocabulary"]) == expected_layers

    counts = Counter(item["desired_layer"] for item in data["data_inventory"])
    expected_counts = dict(data["summary_counts"])
    total = expected_counts.pop("total_items")
    assert len(data["data_inventory"]) == total
    assert counts == expected_counts
    assert data["current_visible_share"]["shown_or_partly_shown_items"] == 17
    assert data["current_visible_share"]["not_shown_or_future_items"] == 19


def test_data_exposure_audit_covers_required_sources() -> None:
    data = _json(AUDIT)
    sources = set(data["source_assets"])

    required = {
        "run_archive/result.json",
        "run_archive/extraction.json",
        "teacher_learning_packet",
        "decision_work_sidecars",
        "data/model_sources/*.md",
        "data/model_sources/manifest.json",
        "data/curation/*.json",
        "data/curation/intervention_semantics/*.json",
        "data/curation/relation_semantics/*.json",
        "data/relationship_graph.json",
        "data/knowledge_graph.json",
        "data/embeddings.db",
        "data/curated/*.json",
        "data/family_semantics/*.json",
        "data/compiled/model_affordances/affordances_v60.json",
        "graph_survival_and_eval_artifacts",
        "conversation_memory_bundle_worktree",
    }
    assert required <= sources


def test_data_exposure_audit_classifies_key_product_and_internal_items() -> None:
    data = _json(AUDIT)
    by_id = {item["id"]: item for item in data["data_inventory"]}

    expected = {
        "selected_run_context": "default_workspace_summary",
        "teacher_lesson": "primary_product_surface",
        "model_pages_selected_run": "primary_product_surface",
        "canonical_model_markdown": "expandable_product_detail",
        "model_detail_local_neighborhood": "expandable_product_detail",
        "extraction_audit": "optional_technical_inspection",
        "conversation_memory_bundle": "agent_memory_export",
        "knowledge_graph": "future_or_suggestion_only",
        "relationship_graph": "future_or_suggestion_only",
        "semantic_neighbors": "future_or_suggestion_only",
        "raw_embeddings": "internal_only",
        "raw_conversation": "private_hidden",
        "private_operator_artifacts": "private_hidden",
    }
    for item_id, layer in expected.items():
        assert by_id[item_id]["desired_layer"] == layer
        assert by_id[item_id]["user_reason"]
        assert by_id[item_id]["presentation_rule"]
        assert by_id[item_id]["do_not_show"]

    assert "Do not imply the selected-run subset is the whole canonical library." in (
        by_id["model_pages_selected_run"]["do_not_show"]
    )
    assert "Do not expose raw affinity" in by_id["model_detail_local_neighborhood"][
        "do_not_show"
    ]
    assert "Do not treat embedding similarity as validated relation semantics." in (
        by_id["semantic_neighbors"]["do_not_show"]
    )


def test_data_exposure_audit_records_graph_substrate_gap() -> None:
    data = _json(AUDIT)
    graph = data["graph_substrate"]

    assert graph["current_visible_graph"]["scope"] == "selected_run_learning_neighborhood"
    assert graph["current_visible_graph"]["full_corpus_graph"] is False
    assert graph["current_visible_graph"]["model_detail_local_neighborhood"] is False
    assert "not evidence that a model has only one relation" in graph[
        "current_visible_graph"
    ]["note"]

    counts = graph["substrate_counts"]
    assert counts["canonical_model_markdown_files"] >= 222
    assert counts["relationship_edges"] >= 1358
    assert counts["knowledge_graph_models"] >= 222
    assert counts["knowledge_graph_edges"] >= 1742
    assert counts["relation_semantics_files"] >= 225

    assert graph["required_graph_modes"] == [
        "selected_run_learning_neighborhood",
        "model_detail_local_neighborhood",
        "filtered_library_graph",
        "future_full_corpus_graph",
    ]
    assert "under-represents the known relation substrate" in graph["gap"]


def test_conversation_memory_worktree_is_classified_without_runtime_wiring() -> None:
    data = _json(AUDIT)
    memory = data["conversation_memory_bundle"]

    assert memory["status"] == "separate_worktree_unmerged"
    assert memory["desired_layer"] == "agent_memory_export"
    assert memory["runtime_default"] is False
    assert memory["provider_or_model_calls"] is False
    assert memory["archive_mutation"] is False
    assert "offline export capability only" in memory["merge_recommendation"]


def test_data_exposure_audit_doc_explains_progression_and_boundaries() -> None:
    text = _read(DOC)

    for phrase in [
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "what starts the experience",
        "what is a primary product surface",
        "what opens as detail",
        "what stays technical",
        "what belongs in an explicit agent memory export",
        "what stays internal or private",
        "The current visible Map is a selected-run learning neighborhood.",
        "It is not a claim that the selected mental model has only one relation.",
        "model-detail local neighborhoods before attempting a global full-corpus graph",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in text


def test_review_json_records_decision_gate_and_non_claims() -> None:
    review = _json(REVIEW)

    assert review["decision_gate"] == "proceed_to_graph_substrate_and_memory_export_design"
    assert review["implemented"]["graph_substrate_gap_called_out"] is True
    assert review["implemented"]["conversation_memory_worktree_classified"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False

    for key in [
        "runs_lolla",
        "invokes_lolla_skill",
        "calls_provider_or_model",
        "creates_new_run",
        "wires_skill_runtime_behavior",
        "mutates_archives",
        "touches_skill_md",
        "touches_scripts_skill",
        "touches_archive_run",
    ]:
        assert review["boundary"][key] is False

    for key in [
        "product_proof",
        "human_validated",
        "answer_correctness",
        "advice_correctness",
        "runtime_integration_authorized",
        "action_authorized",
        "graph_edges_are_proof",
        "embedding_similarity_is_validated_relation_semantics",
    ]:
        assert review["non_claims"][key] is False


def test_markdown_links_and_privacy_markers_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = _read(path)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    combined = "\n".join(_read(path) for path in [DOC, AUDIT, REVIEW])

    assert missing == []
    assert "/" + "Users/" not in combined
    assert "Desktop/" + "Apps" not in combined
    assert "product_proof\": true" not in combined
    assert "human_validated\": true" not in combined
    assert "answer_correctness\": true" not in combined
    assert "advice_correctness\": true" not in combined
    assert "runtime_integration_authorized\": true" not in combined
    assert "action_authorized\": true" not in combined
