import copy
import json
from pathlib import Path

import pytest

from engine.system_b.mental_model_teacher_product_contracts import (
    MENTAL_MODEL_PAGE_SCHEMA_VERSION,
    RELATION_PAGE_SCHEMA_VERSION,
    TEACHER_LESSON_SCHEMA_VERSION,
    VISUAL_GRAPH_SCHEMA_VERSION,
    MentalModelTeacherContractError,
    load_json_object,
    render_contract_json,
    validate_mental_model_page,
    validate_product_object,
    validate_relation_page,
    validate_teacher_lesson,
    validate_visual_graph,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = REPO_ROOT / "docs/product/mental-model-teacher-product-contract-examples-v0.json"
CONTRACT_DOC = REPO_ROOT / "docs/product/mental-model-teacher-product-contracts-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-product-contracts-v0/review.json"
)


def _examples() -> dict:
    return json.loads(EXAMPLES.read_text(encoding="utf-8"))["examples"]


def test_examples_file_contains_all_four_product_contracts() -> None:
    examples = _examples()

    assert examples["mental_model_page"]["schema_version"] == MENTAL_MODEL_PAGE_SCHEMA_VERSION
    assert examples["relation_page"]["schema_version"] == RELATION_PAGE_SCHEMA_VERSION
    assert examples["teacher_lesson"]["schema_version"] == TEACHER_LESSON_SCHEMA_VERSION
    assert examples["visual_graph"]["schema_version"] == VISUAL_GRAPH_SCHEMA_VERSION


def test_valid_example_contracts_pass_specific_validators() -> None:
    examples = _examples()

    assert validate_mental_model_page(examples["mental_model_page"])["model_id"] == (
        "base-rates"
    )
    assert validate_relation_page(examples["relation_page"])["relation_type"] == "ally"
    assert validate_teacher_lesson(examples["teacher_lesson"])["product_proof"] is False
    assert validate_visual_graph(examples["visual_graph"])["graph_scope"] == (
        "lesson_neighborhood"
    )


def test_valid_example_contracts_pass_dispatch_validator() -> None:
    for payload in _examples().values():
        validated = validate_product_object(payload)
        assert validated["schema_version"] == payload["schema_version"]


def test_contracts_require_source_refs_missingness_and_non_claims() -> None:
    page = copy.deepcopy(_examples()["mental_model_page"])

    page.pop("source_refs")
    with pytest.raises(MentalModelTeacherContractError, match="source_refs"):
        validate_mental_model_page(page)

    page = copy.deepcopy(_examples()["mental_model_page"])
    page.pop("missingness")
    with pytest.raises(MentalModelTeacherContractError, match="missingness"):
        validate_mental_model_page(page)

    page = copy.deepcopy(_examples()["mental_model_page"])
    page["non_claims"] = ["not_product_proof"]
    with pytest.raises(MentalModelTeacherContractError, match="missing non_claims"):
        validate_mental_model_page(page)


def test_raw_local_paths_are_rejected() -> None:
    page = copy.deepcopy(_examples()["mental_model_page"])
    page["source_refs"][0]["path"] = "/" + "Users/example/private.md"

    with pytest.raises(MentalModelTeacherContractError, match="repo-relative"):
        validate_mental_model_page(page)


def test_teacher_contract_rejects_product_proof_and_runtime_authorization() -> None:
    lesson = copy.deepcopy(_examples()["teacher_lesson"])
    lesson["product_proof"] = True

    with pytest.raises(MentalModelTeacherContractError, match="product_proof"):
        validate_teacher_lesson(lesson)

    lesson = copy.deepcopy(_examples()["teacher_lesson"])
    lesson["runtime_integration_authorized"] = True

    with pytest.raises(
        MentalModelTeacherContractError,
        match="runtime_integration_authorized",
    ):
        validate_teacher_lesson(lesson)


def test_relation_contract_rejects_overclaiming_relation_language() -> None:
    relation = copy.deepcopy(_examples()["relation_page"])
    relation["plain_language_story"] = "This relation proves the model stack is true."

    with pytest.raises(MentalModelTeacherContractError, match="proof language"):
        validate_relation_page(relation)

    relation = copy.deepcopy(_examples()["relation_page"])
    relation["confidence"] = "proof"

    with pytest.raises(MentalModelTeacherContractError, match="confidence"):
        validate_relation_page(relation)


def test_graph_contract_rejects_rank_affinity_and_edge_proof_language() -> None:
    graph = copy.deepcopy(_examples()["visual_graph"])
    graph["edges"][0]["affinity"] = 0.99

    with pytest.raises(MentalModelTeacherContractError, match="affinity"):
        validate_visual_graph(graph)

    graph = copy.deepcopy(_examples()["visual_graph"])
    graph["edges"][0]["label"] = "proves the better model"

    with pytest.raises(MentalModelTeacherContractError, match="proof"):
        validate_visual_graph(graph)


def test_unsupported_schema_is_rejected() -> None:
    with pytest.raises(MentalModelTeacherContractError, match="unsupported"):
        validate_product_object({"schema_version": "lolla.mental_model_teacher.unknown.v0"})


def test_render_and_load_helpers_keep_json_shape() -> None:
    page = validate_mental_model_page(_examples()["mental_model_page"])
    rendered = render_contract_json(page)

    assert json.loads(rendered)["schema_version"] == MENTAL_MODEL_PAGE_SCHEMA_VERSION
    loaded = load_json_object(EXAMPLES)
    assert loaded["schema"] == "lolla.mental_model_teacher.product_contract_examples.v0"


def test_contract_doc_and_review_preserve_stop_line_and_non_claims() -> None:
    doc = CONTRACT_DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    for phrase in [
        "does not read the substrate",
        "data builders",
        "model page rendering",
        "graph UI",
        "runtime integration",
        "provider/model calls",
    ]:
        assert phrase in doc

    assert review["decision_gate"] == "proceed_to_pilot_model_relation_page_data_builder"
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["runtime_integration_authorized"] is False
    assert review["non_claims"]["graph_edges_are_proof"] is False


def test_examples_do_not_include_local_paths_or_authority_claims() -> None:
    text = EXAMPLES.read_text(encoding="utf-8")

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
