import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/mental-model-teacher-three-case-product-pilot-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-three-case-product-pilot-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"

REQUIRED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}


def _review() -> dict:
    return json.loads(REVIEW.read_text(encoding="utf-8"))


def test_three_case_pilot_is_deferred_when_teacher_sources_are_missing() -> None:
    review = _review()

    assert review["schema"] == "lolla.mental_model_teacher.three_case_product_pilot_review.v0"
    assert review["status"] == "deferred_missing_teacher_case_artifacts_on_current_main"
    assert review["decision_gate"] == "deferred_until_teacher_offline_package_merged"
    assert review["current_main_assessment"]["teacher_three_case_source_package_present"] is False
    assert review["current_main_assessment"]["decision_work_case_artifacts_present"] is True
    assert review["current_main_assessment"]["decision_work_artifacts_used_as_teacher_source"] is False


def test_required_cases_are_all_blocked_without_generated_outputs() -> None:
    review = _review()
    cases = {case["case_id"]: case for case in review["required_cases"]}

    assert set(cases) == REQUIRED_CASES
    for case in cases.values():
        assert case["teacher_artifacts_found_on_current_main"] is False
        assert case["decision_work_artifacts_found_on_current_main"] is True
        assert case["lesson_page_generated"] is False
        assert case["graph_neighborhood_generated"] is False
        assert case["status"] == "deferred_missing_teacher_source"


def test_review_names_external_source_without_importing_or_merging_it() -> None:
    review = _review()
    source = review["external_source_candidate"]
    boundary = review["boundary_decision"]

    assert source["observed"] is True
    assert source["worktree"] == "/private/tmp/lolla-teacher-package-worktree"
    assert source["branch"] == "feature/mental-model-teacher-offline-review-package-v2"
    assert source["commit"] == "1ebfe24f6ceef8b0481f70f718e3607e31d1e1e8"
    assert source["package_root"] == (
        "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2/"
    )
    assert source["imported_in_this_pr"] is False
    assert source["merged_in_this_pr"] is False
    assert boundary["merge_external_branch_in_this_pr"] is False
    assert boundary["generate_from_unmerged_external_package"] is False


def test_missing_artifact_patterns_are_teacher_specific() -> None:
    review = _review()
    patterns = "\n".join(review["missing_required_artifact_patterns"])

    assert "mental-model-teacher-knowledge-mesh-v2/<case-id>" in patterns
    for artifact in [
        "mental_model_teacher_lesson.json",
        "mental_model_teacher_card.md",
        "mental_model_teacher.md",
        "mental_model_teacher_model_deep_dive.json",
        "mental_model_teacher_relation_deep_dive.json",
        "mental_model_teacher_practice_lab.json",
        "mental_model_teacher_okf_manifest.json",
    ]:
        assert artifact in patterns


def test_doc_explains_why_decision_work_is_not_a_substitute() -> None:
    doc = DOC.read_text(encoding="utf-8")
    normalized_doc = " ".join(doc.split())

    assert "Decision Work and evaluation artifacts" in doc
    assert "are not Teacher lesson artifacts" in doc
    assert (
        "Reusing Decision Work outputs here would collapse the product boundary"
        in normalized_doc
    )
    assert "not generated" in doc.lower()
    assert "deferred_until_teacher_offline_package_merged" in doc
    assert "ceo-remove-founding-cofounder" in doc
    assert "must teach reasoning moves without implying" in normalized_doc


def test_pr_p9_preserves_non_claim_boundaries() -> None:
    review = _review()
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [DOC, REVIEW]
    )

    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["runtime_integration_authorized"] is False
    assert review["non_claims"]["agent_or_automatic_action_authorized"] is False
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text


def test_readme_links_pr_p9_doc_and_markdown_links_resolve() -> None:
    index = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-three-case-product-pilot-v0.md" in index

    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    assert missing == []
