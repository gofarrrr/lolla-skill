import copy
import json
from pathlib import Path

import pytest

from observatory.product_views import (
    ADVANCED_AUDIT_INDEX_SCHEMA_VERSION,
    GRAPH_NEIGHBORHOOD_SCHEMA_VERSION,
    LEARNING_PACKET_SCHEMA_VERSION,
    MODEL_PAGE_SCHEMA_VERSION,
    OUTCOME_SUMMARY_SCHEMA_VERSION,
    PORTABLE_RENDERING_DIRECTION,
    PRIMARY_SURFACES,
    RECEIPT_SUMMARY_SCHEMA_VERSION,
    RELATION_PAGE_SCHEMA_VERSION,
    SELECTED_RUN_SUMMARY_SCHEMA_VERSION,
    WORKSPACE_SCHEMA_VERSION,
    ObservatoryProductViewError,
    load_json_object,
    render_view_json,
    validate_advanced_audit_index,
    validate_graph_neighborhood,
    validate_learning_packet,
    validate_model_page,
    validate_outcome_summary,
    validate_product_view,
    validate_receipt_summary,
    validate_relation_page,
    validate_selected_run_summary,
    validate_workspace,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = (
    REPO_ROOT
    / "docs/product/observatory-portable-product-view-contract-examples-v0.json"
)
CONTRACT_DOC = (
    REPO_ROOT / "docs/product/observatory-portable-product-view-contracts-v0.md"
)
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-portable-product-view-contracts-v0/review.json"
)


def _examples() -> dict:
    return json.loads(EXAMPLES.read_text(encoding="utf-8"))["examples"]


def test_examples_file_contains_all_product_view_contracts() -> None:
    examples = _examples()

    assert examples["workspace"]["schema_version"] == WORKSPACE_SCHEMA_VERSION
    assert (
        examples["selected_run_summary"]["schema_version"]
        == SELECTED_RUN_SUMMARY_SCHEMA_VERSION
    )
    assert examples["outcome_summary"]["schema_version"] == OUTCOME_SUMMARY_SCHEMA_VERSION
    assert examples["learning_packet"]["schema_version"] == LEARNING_PACKET_SCHEMA_VERSION
    assert examples["model_page"]["schema_version"] == MODEL_PAGE_SCHEMA_VERSION
    assert examples["relation_page"]["schema_version"] == RELATION_PAGE_SCHEMA_VERSION
    assert (
        examples["graph_neighborhood"]["schema_version"]
        == GRAPH_NEIGHBORHOOD_SCHEMA_VERSION
    )
    assert examples["receipt_summary"]["schema_version"] == RECEIPT_SUMMARY_SCHEMA_VERSION
    assert (
        examples["advanced_audit_index"]["schema_version"]
        == ADVANCED_AUDIT_INDEX_SCHEMA_VERSION
    )


def test_valid_examples_pass_specific_validators() -> None:
    examples = _examples()

    assert validate_selected_run_summary(examples["selected_run_summary"])[
        "primary_surfaces"
    ] == list(PRIMARY_SURFACES)
    assert validate_outcome_summary(examples["outcome_summary"])["model_chips"][0][
        "model_id"
    ] == "opportunity-cost"
    assert validate_learning_packet(examples["learning_packet"])[
        "product_proof"
    ] is False
    assert validate_model_page(examples["model_page"])["model_id"] == "opportunity-cost"
    assert validate_relation_page(examples["relation_page"])["confidence"] == "unknown"
    assert validate_graph_neighborhood(examples["graph_neighborhood"])[
        "search_enabled"
    ] is True
    assert validate_receipt_summary(examples["receipt_summary"])[
        "process_brief_status"
    ] == "not_requested"
    assert validate_advanced_audit_index(examples["advanced_audit_index"])[
        "artifact_statuses"
    ][1]["status"] == "not_requested"


def test_valid_examples_pass_dispatch_validator() -> None:
    examples = _examples()

    for key in (
        "workspace",
        "selected_run_summary",
        "outcome_summary",
        "learning_packet",
        "model_page",
        "relation_page",
        "graph_neighborhood",
        "receipt_summary",
        "advanced_audit_index",
    ):
        validated = validate_product_view(examples[key])
        assert validated["schema_version"] == examples[key]["schema_version"]


def test_workspace_contract_composes_portable_surfaces() -> None:
    workspace = validate_workspace(_examples()["workspace"])

    assert workspace["rendering_direction"] == PORTABLE_RENDERING_DIRECTION
    assert workspace["primary_surfaces"] == list(PRIMARY_SURFACES)
    assert workspace["advanced_surface"] == "Advanced Audit"
    assert workspace["learning_packet"]["thinking_move"] == (
        "Separate the case for learning from the case for scaling."
    )
    assert workspace["model_pages"][0]["source_refs"][0]["source_type"] == (
        "canonical_model_markdown"
    )
    assert workspace["relation_pages"][0]["relation_type"] == "ally"


def test_contracts_require_source_refs_missingness_and_non_claims() -> None:
    page = copy.deepcopy(_examples()["model_page"])

    page.pop("source_refs")
    with pytest.raises(ObservatoryProductViewError, match="source_refs"):
        validate_model_page(page)

    page = copy.deepcopy(_examples()["model_page"])
    page.pop("missingness")
    with pytest.raises(ObservatoryProductViewError, match="missingness"):
        validate_model_page(page)

    page = copy.deepcopy(_examples()["model_page"])
    page["non_claims"] = ["not_product_proof"]
    with pytest.raises(ObservatoryProductViewError, match="missing non_claims"):
        validate_model_page(page)


def test_raw_local_paths_and_external_hrefs_are_rejected() -> None:
    page = copy.deepcopy(_examples()["model_page"])
    page["source_refs"][0]["path"] = "/" + "Users/example/private.md"

    with pytest.raises(ObservatoryProductViewError, match="repo-relative"):
        validate_model_page(page)

    page = copy.deepcopy(_examples()["model_page"])
    page["selected_run_backlinks"][0]["href"] = "https://example.com/model"

    with pytest.raises(ObservatoryProductViewError, match="internal href"):
        validate_model_page(page)


def test_learning_packet_rejects_product_proof_and_runtime_authorization() -> None:
    lesson = copy.deepcopy(_examples()["learning_packet"])
    lesson["product_proof"] = True

    with pytest.raises(ObservatoryProductViewError, match="product_proof"):
        validate_learning_packet(lesson)

    lesson = copy.deepcopy(_examples()["learning_packet"])
    lesson["runtime_integration_authorized"] = True

    with pytest.raises(
        ObservatoryProductViewError,
        match="runtime_integration_authorized",
    ):
        validate_learning_packet(lesson)


def test_workspace_rejects_non_portable_direction_and_svelte_revival() -> None:
    workspace = copy.deepcopy(_examples()["workspace"])
    workspace["rendering_direction"] = "legacy_svelte_root_app"

    with pytest.raises(ObservatoryProductViewError, match="rendering_direction"):
        validate_workspace(workspace)

    workspace = copy.deepcopy(_examples()["workspace"])
    workspace["svelte_revival_authorized"] = True

    with pytest.raises(ObservatoryProductViewError, match="svelte_revival_authorized"):
        validate_workspace(workspace)


def test_workspace_rejects_wrong_primary_surfaces() -> None:
    workspace = copy.deepcopy(_examples()["workspace"])
    workspace["primary_surfaces"] = ["Cases", "Families"]

    with pytest.raises(ObservatoryProductViewError, match="primary_surfaces"):
        validate_workspace(workspace)


def test_relation_rejects_overclaiming_and_certified_confidence() -> None:
    relation = copy.deepcopy(_examples()["relation_page"])
    relation["plain_language_story"] = "This relation proves the run is correct."

    with pytest.raises(ObservatoryProductViewError, match="relation-proof language"):
        validate_relation_page(relation)

    relation = copy.deepcopy(_examples()["relation_page"])
    relation["confidence"] = "certified"

    with pytest.raises(ObservatoryProductViewError, match="confidence"):
        validate_relation_page(relation)


def test_graph_rejects_affinity_and_edge_proof_language() -> None:
    graph = copy.deepcopy(_examples()["graph_neighborhood"])
    graph["edges"][0]["affinity"] = 0.99

    with pytest.raises(ObservatoryProductViewError, match="affinity"):
        validate_graph_neighborhood(graph)

    graph = copy.deepcopy(_examples()["graph_neighborhood"])
    graph["edges"][0]["navigation_label"] = "proves the better model"

    with pytest.raises(ObservatoryProductViewError, match="proof"):
        validate_graph_neighborhood(graph)


def test_unknown_schema_is_rejected() -> None:
    with pytest.raises(ObservatoryProductViewError, match="unsupported"):
        validate_product_view({"schema_version": "lolla.observatory.unknown.v0"})


def test_render_and_load_helpers_keep_json_shape() -> None:
    workspace = validate_workspace(_examples()["workspace"])
    rendered = render_view_json(workspace)

    assert json.loads(rendered)["schema_version"] == WORKSPACE_SCHEMA_VERSION
    loaded = load_json_object(EXAMPLES)
    assert loaded["schema"] == "lolla.observatory.portable_product_view_contract_examples.v0"


def test_doc_readme_and_review_preserve_direction_stop_line_and_non_claims() -> None:
    doc = CONTRACT_DOC.read_text(encoding="utf-8")
    doc_flat = " ".join(doc.split())
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    for phrase in [
        "portable Python/server HTML path",
        "does not read run archives",
        "root workspace rendering",
        "legacy Svelte source changes",
        "compiled bundle edits",
        "raw Markdown is not the product UI",
        "proceed_to_observatory_portable_view_model_adapters",
    ]:
        assert phrase in doc_flat

    assert "Observatory Portable Product View Contracts" in readme
    assert "observatory-portable-product-view-contracts-v0.md" in readme
    assert "observatory-portable-product-view-contract-examples-v0.json" in readme

    assert (
        review["decision_gate"]
        == "proceed_to_observatory_portable_view_model_adapters"
    )
    assert review["rendering_direction"] == PORTABLE_RENDERING_DIRECTION
    assert review["primary_surfaces"] == list(PRIMARY_SURFACES)
    assert review["single_home_rules"]["canonical_model_explanation"] == "Models"
    assert review["single_home_rules"]["raw_telemetry"] == "Advanced Audit"
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["provider_or_model_calls"] is False
    assert review["boundary"]["runtime_behavior_changed"] is False
    assert review["boundary"]["ui_rendering_added"] is False
    assert review["boundary"]["svelte_revival_authorized"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["graph_edges_are_proof"] is False


def test_examples_do_not_include_local_paths_or_authority_claims() -> None:
    text = EXAMPLES.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
    assert "svelte_revival_authorized\": true" not in text
