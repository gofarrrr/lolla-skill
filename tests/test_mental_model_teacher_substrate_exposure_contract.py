import json
from pathlib import Path

from engine.system_b.mental_model_teacher_substrate_inventory import (
    ALLOWED_CLASSIFICATIONS,
    build_inventory,
    main,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY = REPO_ROOT / "docs/product/mental-model-teacher-substrate-exposure-contract-v0.json"
REPORT = REPO_ROOT / "docs/product/mental-model-teacher-substrate-exposure-contract-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-substrate-exposure-contract-v0/review.json"
)

REQUIRED_ASSET_IDS = {
    "canonical_model_markdown",
    "model_source_manifest",
    "model_source_hashes",
    "activation_curation",
    "intervention_semantics",
    "relation_semantics",
    "relationship_graph",
    "knowledge_graph",
    "embeddings_db",
    "curated_chunks",
    "family_semantics",
    "v60_model_affordances",
    "relation_graph_code",
    "activation_matcher_code",
    "graph_survival_eval_artifacts",
    "model_affordance_validation_code",
    "teacher_artifacts",
}


def _asset(summary: dict, asset_id: str) -> dict:
    matches = [asset for asset in summary["assets"] if asset["asset_id"] == asset_id]
    assert len(matches) == 1
    return matches[0]


def test_policy_and_report_files_exist_and_are_indexed() -> None:
    assert POLICY.exists()
    assert REPORT.exists()
    assert REVIEW.exists()

    index = README.read_text(encoding="utf-8")
    assert "mental-model-teacher-substrate-exposure-contract-v0.md" in index
    assert "mental-model-teacher-substrate-exposure-contract-v0.json" in index


def test_policy_json_has_required_assets_and_classifications() -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))

    assert policy["schema"] == "lolla.mental_model_teacher.substrate_exposure_policy.v0"
    assert policy["decision_gate"] == "proceed_to_user_facing_model_relation_contracts"
    assert set(policy["classification_vocabulary"]) == ALLOWED_CLASSIFICATIONS

    asset_ids = {asset["asset_id"] for asset in policy["assets"]}
    assert REQUIRED_ASSET_IDS <= asset_ids

    classifications = {asset["classification"] for asset in policy["assets"]}
    assert classifications == ALLOWED_CLASSIFICATIONS


def test_inventory_summary_covers_current_substrate_counts() -> None:
    summary = build_inventory(REPO_ROOT)

    assert summary["schema"] == "lolla.mental_model_teacher.substrate_inventory_summary.v0"
    assert summary["decision_gate"] == "proceed_to_user_facing_model_relation_contracts"
    assert summary["missing_required_asset_ids"] == []
    assert summary["asset_count"] >= len(REQUIRED_ASSET_IDS)

    assert _asset(summary, "canonical_model_markdown")["discovered"]["counts"][
        "markdown_files"
    ] >= 222
    assert _asset(summary, "model_source_manifest")["discovered"]["counts"][
        "manifest_files"
    ] >= 222
    assert _asset(summary, "activation_curation")["discovered"]["counts"][
        "direct_json_files"
    ] >= 220
    assert _asset(summary, "intervention_semantics")["discovered"]["counts"][
        "json_files"
    ] >= 220
    assert _asset(summary, "relation_semantics")["discovered"]["counts"][
        "json_files"
    ] >= 220
    assert _asset(summary, "knowledge_graph")["discovered"]["counts"]["models"] >= 222
    assert _asset(summary, "knowledge_graph")["discovered"]["counts"]["edges"] >= 1700
    assert _asset(summary, "relationship_graph")["discovered"]["counts"]["edges"] >= 1300
    assert _asset(summary, "relationship_graph")["discovered"]["counts"][
        "curated_edges"
    ] >= 1300
    assert _asset(summary, "embeddings_db")["discovered"]["counts"]["bytes"] > 1_000_000
    assert _asset(summary, "curated_chunks")["discovered"]["counts"]["json_files"] >= 4
    assert _asset(summary, "family_semantics")["discovered"]["counts"]["json_files"] >= 20
    assert _asset(summary, "v60_model_affordances")["discovered"]["counts"][
        "model_records"
    ] >= 222
    assert _asset(summary, "v60_model_affordances")["discovered"]["counts"][
        "affordances"
    ] >= 300
    assert _asset(summary, "graph_survival_eval_artifacts")["discovered"]["counts"][
        "required_code_files_present"
    ] == 2


def test_exposure_classifications_preserve_product_boundaries() -> None:
    summary = build_inventory(REPO_ROOT)

    expected = {
        "canonical_model_markdown": "product-safe-after-translation",
        "model_source_manifest": "product-safe-after-translation",
        "model_source_hashes": "product-safe",
        "activation_curation": "product-safe-after-translation",
        "intervention_semantics": "product-safe-after-translation",
        "relation_semantics": "product-safe-after-translation",
        "relationship_graph": "product-safe-after-translation",
        "knowledge_graph": "future/suggestion-only",
        "embeddings_db": "internal-only",
        "curated_chunks": "product-safe-after-translation",
        "family_semantics": "future/suggestion-only",
        "v60_model_affordances": "future/suggestion-only",
        "relation_graph_code": "internal-only",
        "activation_matcher_code": "internal-only",
        "graph_survival_eval_artifacts": "internal-only",
        "model_affordance_validation_code": "internal-only",
        "teacher_artifacts": "product-safe-after-translation",
    }

    for asset_id, classification in expected.items():
        assert _asset(summary, asset_id)["classification"] == classification

    non_claims = summary["non_claims"]
    assert non_claims["product_proof"] is False
    assert non_claims["human_validated"] is False
    assert non_claims["runtime_integration_authorized"] is False
    assert non_claims["graph_edges_are_proof"] is False
    assert non_claims["embedding_similarity_is_validated_relation_semantics"] is False


def test_manifest_path_marker_is_detected_without_leaking_path() -> None:
    summary = build_inventory(REPO_ROOT)
    manifest = _asset(summary, "model_source_manifest")

    assert manifest["discovered"]["raw_contains_local_path_marker"] is False

    rendered = json.dumps(summary, sort_keys=True)
    assert "/" + "Users/" not in rendered
    assert "Desktop/" + "Apps" not in rendered


def test_teacher_artifacts_are_optional_and_not_faked() -> None:
    summary = build_inventory(REPO_ROOT)
    teacher = _asset(summary, "teacher_artifacts")

    assert teacher["required"] is False
    assert teacher["discovered"]["status"] in {"present", "missing_optional"}
    if teacher["discovered"]["status"] == "missing_optional":
        assert teacher["discovered"]["counts"]["artifact_files"] == 0
        assert "No checked-in Teacher artifact directory" in teacher["discovered"][
            "missingness"
        ]


def test_slice_stops_before_product_contracts_renderers_and_graph_ui() -> None:
    policy_text = POLICY.read_text(encoding="utf-8")
    report_text = REPORT.read_text(encoding="utf-8")
    combined = policy_text + "\n" + report_text

    for required_stop in [
        "Mental Model Product Page contracts",
        "Relation Product Page contracts",
        "Teacher Lesson Product contracts",
        "Visual Graph contracts",
        "page rendering",
        "graph UI",
        "runtime hooks",
        "provider/model calls",
    ]:
        assert required_stop in combined

    for contract_field in [
        "one_sentence_meaning",
        "plain_language_story",
        "practice_rep",
        "layout_hint",
    ]:
        assert contract_field not in combined


def test_review_json_matches_pr_p2_gate_and_boundaries() -> None:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert (
        review["schema"]
        == "lolla.mental_model_teacher.substrate_exposure_contract_review.v0"
    )
    assert review["decision_gate"] == "proceed_to_user_facing_model_relation_contracts"
    assert set(review["covered_asset_ids"]) == REQUIRED_ASSET_IDS
    assert "teacher_artifacts" in review["known_missingness"]
    assert "product page contracts" in review["stop_before"]

    non_claims = review["non_claims"]
    assert non_claims["product_proof"] is False
    assert non_claims["human_validated"] is False
    assert non_claims["answer_correctness"] is False
    assert non_claims["advice_correctness"] is False
    assert non_claims["runtime_integration_authorized"] is False


def test_inventory_cli_can_write_json_summary(tmp_path: Path) -> None:
    output = tmp_path / "inventory-summary.json"

    status = main(["--root", str(REPO_ROOT), "--policy", str(POLICY), "--output", str(output)])

    assert status == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema"] == "lolla.mental_model_teacher.substrate_inventory_summary.v0"
    assert data["missing_required_asset_ids"] == []
