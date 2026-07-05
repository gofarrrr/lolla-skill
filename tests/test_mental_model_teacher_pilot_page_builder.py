import json
from pathlib import Path

import pytest

from engine.system_b.mental_model_teacher_pilot_page_builder import (
    DEFAULT_MODEL_IDS,
    PILOT_SCHEMA_VERSION,
    MentalModelTeacherPilotBuilderError,
    build_pilot_page_data,
    main,
)
from engine.system_b.mental_model_teacher_product_contracts import (
    validate_mental_model_page,
    validate_relation_page,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/mental-model-teacher-pilot-page-data-builder-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-pilot-page-data-builder-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"


def test_builder_emits_default_pilot_package_shape() -> None:
    package = build_pilot_page_data(REPO_ROOT)

    assert package["schema_version"] == PILOT_SCHEMA_VERSION
    assert package["builder_mode"] == "deterministic_offline"
    assert package["pilot_scope"]["model_ids"] == list(DEFAULT_MODEL_IDS)
    assert package["build_review"]["model_page_count"] == 3
    assert package["build_review"]["relation_page_count"] == 2
    assert package["build_review"]["relation_ids"] == [
        "base-rates__ally__scientific-method-evidence-testing",
        "base-rates__ally__system-2",
    ]


def test_generated_pages_validate_against_pr_p3_contracts() -> None:
    package = build_pilot_page_data(REPO_ROOT)

    for page in package["model_pages"]:
        validated = validate_mental_model_page(page)
        assert validated["model_id"] in DEFAULT_MODEL_IDS

    for page in package["relation_pages"]:
        validated = validate_relation_page(page)
        assert validated["source_model_id"] in DEFAULT_MODEL_IDS
        assert validated["target_model_id"] in DEFAULT_MODEL_IDS


def test_builder_preserves_source_refs_and_hashes() -> None:
    package = build_pilot_page_data(REPO_ROOT)

    for page in package["model_pages"]:
        paths = {ref["path"] for ref in page["source_refs"]}
        model_id = page["model_id"]
        assert f"data/curation/{model_id}.json" in paths
        assert f"data/curation/intervention_semantics/{model_id}.json" in paths
        assert len(page["source_hashes"]) == 1
        for path in paths:
            assert not path.startswith("/")
            assert (REPO_ROOT / path).exists()
        for path in page["source_hashes"]:
            assert not path.startswith("/")
            assert (REPO_ROOT / path).exists()


def test_builder_preserves_missingness_instead_of_inventing_copy() -> None:
    package = build_pilot_page_data(REPO_ROOT)

    for page in package["model_pages"]:
        assert page["common_misuse"] == []
        assert page["practice_prompts"] == []
        assert page["missingness"]["status"] == "partial"
        assert "common_misuse" in page["missingness"]["missing_fields"]
        assert "practice_prompts" in page["missingness"]["missing_fields"]

    for relation in package["relation_pages"]:
        assert relation["missingness"]["status"] == "partial"
        assert "source_specific_misread_risk" in relation["missingness"][
            "missing_fields"
        ]
        assert "source_specific_practice_prompt" in relation["missingness"][
            "missing_fields"
        ]
        assert "not proof" in relation["misread_risk"]


def test_builder_does_not_use_embeddings_teacher_artifacts_or_runtime_claims() -> None:
    package = build_pilot_page_data(REPO_ROOT)
    review = package["build_review"]

    assert review["checked_in_teacher_artifacts_used"] is False
    assert review["embeddings_used"] is False
    assert review["runtime_integration_authorized"] is False
    assert review["product_proof"] is False

    non_claims = package["non_claims"]
    assert non_claims["product_proof"] is False
    assert non_claims["human_validated"] is False
    assert non_claims["runtime_integration_authorized"] is False
    assert non_claims["embedding_similarity_is_validated_relation_semantics"] is False


def test_builder_output_has_no_local_paths_or_raw_manifest_provenance() -> None:
    package = build_pilot_page_data(REPO_ROOT)
    rendered = json.dumps(package, sort_keys=True)

    assert "/" + "Users/" not in rendered
    assert "Desktop/" + "Apps" not in rendered
    assert "copied_from" not in rendered


def test_cli_writes_explicit_temp_output(tmp_path: Path) -> None:
    output = tmp_path / "pilot-pages.json"

    status = main(["--root", str(REPO_ROOT), "--output", str(output)])

    assert status == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema_version"] == PILOT_SCHEMA_VERSION
    assert data["build_review"]["model_page_count"] == 3


def test_unknown_model_is_a_clear_builder_error() -> None:
    with pytest.raises(MentalModelTeacherPilotBuilderError, match="missing manifest"):
        build_pilot_page_data(REPO_ROOT, model_ids=("not-a-real-model",))


def test_pr_p4_docs_and_review_preserve_boundary_and_gate() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    index = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-pilot-page-data-builder-v0.md" in index
    assert review["decision_gate"] == "proceed_to_static_model_relation_page_renderer"
    assert review["generated_artifact_policy"].startswith("Generated pilot page data")
    for phrase in [
        "does not use embeddings",
        "does not call providers or model APIs",
        "does not render Markdown or HTML pages",
        "does not create graph UI",
        "does not wire runtime",
        "model page rendering",
        "relation page rendering",
        "graph UI",
    ]:
        assert phrase in doc
