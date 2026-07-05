import json
from pathlib import Path

import pytest

from engine.system_b.mental_model_teacher_lesson_graph_builder import (
    LESSON_GRAPH_MANIFEST_SCHEMA_VERSION,
    build_fixture_lesson_graph,
    write_fixture_lesson_graph_package,
)
from engine.system_b.mental_model_teacher_product_contracts import (
    VISUAL_GRAPH_SCHEMA_VERSION,
    MentalModelTeacherContractError,
    validate_visual_graph,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
GRAPH_DIR = REPO_ROOT / "docs/product/mental-model-teacher-lesson-graph-v0"
GRAPH_JSON = GRAPH_DIR / "contract-fixture-base-rates-system-2.graph.json"
DOC = REPO_ROOT / "docs/product/mental-model-teacher-lesson-graph-data-builder-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-lesson-graph-data-builder-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"


def test_builder_writes_temp_graph_package(tmp_path: Path) -> None:
    manifest = write_fixture_lesson_graph_package(REPO_ROOT, tmp_path)

    assert manifest["schema_version"] == LESSON_GRAPH_MANIFEST_SCHEMA_VERSION
    assert manifest["graph_count"] == 1
    assert manifest["browser_graph_ui_built"] is False
    assert manifest["embeddings_used"] is False
    assert manifest["runtime_integration_authorized"] is False
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "contract-fixture-base-rates-system-2.graph.json").exists()


def test_checked_in_graph_manifest_matches_expected_package() -> None:
    manifest = json.loads((GRAPH_DIR / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["schema_version"] == LESSON_GRAPH_MANIFEST_SCHEMA_VERSION
    assert manifest["graph_data_status"] == (
        "fixture_lesson_neighborhood_graph_data_ready_for_review"
    )
    assert manifest["graph_count"] == 1
    assert manifest["graphs"][0]["node_count"] == 2
    assert manifest["graphs"][0]["edge_count"] == 1
    assert manifest["browser_graph_ui_built"] is False
    assert manifest["provider_or_model_calls_used"] is False
    assert manifest["non_claims"]["graph_edges_are_proof"] is False
    assert manifest["non_claims"][
        "embedding_similarity_is_validated_relation_semantics"
    ] is False


def test_checked_in_graph_matches_visual_graph_contract() -> None:
    graph = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    validated = validate_visual_graph(graph)

    assert validated["schema_version"] == VISUAL_GRAPH_SCHEMA_VERSION
    assert validated["graph_scope"] == "lesson_neighborhood"
    assert validated["graph_id"] == (
        "lesson-neighborhood-contract-fixture-base-rates-system-2"
    )
    assert validated["default_focus"] == "base-rates"
    assert len(validated["nodes"]) == 2
    assert len(validated["edges"]) == 1


def test_graph_nodes_come_from_selected_model_pages_and_links_resolve() -> None:
    graph = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    nodes = {node["node_id"]: node for node in graph["nodes"]}

    assert set(nodes) == {"base-rates", "system-2"}
    assert nodes["base-rates"]["label"] == "Base Rates"
    assert nodes["system-2"]["label"] == "System 2"
    assert nodes["base-rates"]["source_status"] == "draft"
    assert nodes["base-rates"]["missingness_status"] == "partial"

    for node in nodes.values():
        href = GRAPH_JSON.parent / node["href"]
        assert href.resolve().exists()


def test_graph_edge_comes_from_relation_page_and_click_resolves() -> None:
    graph = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    edge = graph["edges"][0]

    assert edge["edge_id"] == "base-rates__ally__system-2"
    assert edge["source_node_id"] == "base-rates"
    assert edge["target_node_id"] == "system-2"
    assert edge["relation_type"] == "ally"
    assert edge["href"] == (
        "../mental-model-teacher-pilot-render-v0/relations/"
        "base-rates__ally__system-2.md"
    )
    assert (GRAPH_JSON.parent / edge["href"]).resolve().exists()
    assert edge["confidence"] == "high"
    assert edge["source_status"] == "draft"
    assert edge["missingness_status"] == "partial"

    for forbidden_key in ("affinity", "rank", "embedding_similarity", "score"):
        assert forbidden_key not in edge


def test_visual_graph_contract_rejects_forbidden_edge_scoring_fields() -> None:
    graph = build_fixture_lesson_graph(REPO_ROOT)
    graph["edges"][0]["embedding_similarity"] = 0.91

    with pytest.raises(MentalModelTeacherContractError, match="embedding_similarity"):
        validate_visual_graph(graph)


def test_graph_preserves_missingness_source_artifacts_and_non_claims() -> None:
    graph = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))

    assert graph["missingness"]["status"] == "partial"
    assert "real_case_artifact" in graph["missingness"]["missing_fields"]
    assert "browser_graph_ui" in graph["missingness"]["missing_fields"]
    assert "rendered_layout" in graph["missingness"]["missing_fields"]
    assert {
        artifact["path"] for artifact in graph["source_artifacts"]
    } >= {
        "docs/product/mental-model-teacher-product-contract-examples-v0.json",
        "docs/product/mental-model-teacher-pilot-render-v0/manifest.json",
        "docs/product/mental-model-teacher-lesson-render-v0/manifest.json",
    }
    for non_claim in [
        "not_product_proof",
        "not_human_validation",
        "not_answer_correctness",
        "not_advice_correctness",
        "not_runtime_integration",
        "not_action_authorization",
        "graph_is_navigation_not_proof",
        "edge_is_not_proof",
    ]:
        assert non_claim in graph["non_claims"]


def test_graph_package_has_no_local_paths_or_runtime_claims() -> None:
    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in GRAPH_DIR.rglob("*")
        if path.is_file()
    )

    assert "/" + "Users/" not in rendered
    assert "Desktop/" + "Apps" not in rendered
    assert "runtime_integration_authorized\": true" not in rendered
    assert "product_proof\": true" not in rendered
    assert "human_validated\": true" not in rendered
    assert "\"embedding_similarity\":" not in rendered
    assert "\"affinity\"" not in rendered
    assert "\"rank\"" not in rendered
    assert "\"score\"" not in rendered


def test_builder_doc_and_review_preserve_pr_p7_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    index = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-lesson-graph-data-builder-v0.md" in index
    assert "mental-model-teacher-lesson-graph-v0/manifest.json" in index
    assert review["decision_gate"] == "proceed_to_static_visual_graph_prototype"
    assert review["graph_counts"]["nodes"] == 2
    assert review["graph_counts"]["edges"] == 1
    assert review["input_status"]["embeddings_used"] is False
    assert review["input_status"]["relationship_graph_affinity_used"] is False

    for phrase in [
        "does not create browser graph UI",
        "does not build a full-corpus graph",
        "does not use embeddings",
        "does not expose relationship-graph affinity or rank",
        "does not call providers or model APIs",
        "does not wire runtime",
        "browser graph UI",
    ]:
        assert phrase in doc
