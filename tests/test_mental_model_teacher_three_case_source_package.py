import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2"
)
DOC = REPO_ROOT / "docs/product/mental-model-teacher-three-case-source-package-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-three-case-source-package-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"

REQUIRED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}

REQUIRED_CASE_ARTIFACTS = {
    "case_review.json",
    "mental_model_teacher_lesson.json",
    "mental_model_teacher_card.md",
    "mental_model_teacher.md",
    "mental_model_teacher_model_deep_dive.json",
    "mental_model_teacher_model_deep_dive.md",
    "mental_model_teacher_relation_deep_dive.json",
    "mental_model_teacher_relation_deep_dive.md",
    "mental_model_teacher_practice_lab.json",
    "mental_model_teacher_practice_lab.md",
    "mental_model_teacher_okf_manifest.json",
    "mental_model_teacher_okf_conformance.json",
}

PRIVATE_MARKERS = (
    "/" + "Users/",
    "Desktop/" + "Apps",
    "SEC" + "RET",
    "raw_message_" + "content",
    "fabricated_" + "passages",
    "FULL ASSISTANT " + "REASONING",
    "client_" + "secret",
    "api_" + "key",
    "pass" + "word",
)


def _review() -> dict:
    return json.loads(REVIEW.read_text(encoding="utf-8"))


def test_source_package_review_records_narrow_import_scope() -> None:
    review = _review()

    assert review["schema"] == "lolla.mental_model_teacher.three_case_source_package_review.v0"
    assert review["status"] == "source_package_imported_for_product_pilot_retry"
    assert review["decision_gate"] == "proceed_to_three_case_teacher_product_pilot_retry"
    assert review["source_package"]["imported_root"] == (
        "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2/"
    )
    assert review["source_package"]["imported_case_count"] == 3
    assert review["source_package"]["imported_file_count"] == 122
    assert review["source_package"]["imported_scope"] == "three_case_directories_only"
    assert review["source_package"]["package_level_review_artifacts_imported"] is False


def test_external_branch_was_not_merged_and_runtime_files_were_not_imported() -> None:
    source = _review()["external_source_candidate"]

    assert source["worktree"] == "/private/tmp/lolla-teacher-package-worktree"
    assert source["branch"] == "feature/mental-model-teacher-offline-review-package-v2"
    assert source["commit"] == "1ebfe24f6ceef8b0481f70f718e3607e31d1e1e8"
    assert source["branch_merged_in_this_pr"] is False
    assert source["engine_modules_imported"] is False
    assert source["scripts_imported"] is False
    assert source["coach_artifacts_imported"] is False


def test_three_required_case_directories_and_teacher_artifacts_exist() -> None:
    case_dirs = {
        path.name
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir()
    }

    assert case_dirs == REQUIRED_CASES

    for case_id in REQUIRED_CASES:
        case_dir = SOURCE_ROOT / case_id
        present = {path.relative_to(case_dir).as_posix() for path in case_dir.rglob("*") if path.is_file()}
        assert REQUIRED_CASE_ARTIFACTS <= present
        assert (case_dir / "okf/mental_model_teacher/cases").is_dir()
        assert (case_dir / "okf/mental_model_teacher/models").is_dir()
        assert (case_dir / "okf/mental_model_teacher/relations").is_dir()
        assert (case_dir / "okf/mental_model_teacher/practice").is_dir()


def test_package_level_review_and_human_validation_artifacts_are_excluded() -> None:
    excluded = _review()["intentionally_excluded_package_level_artifacts"]

    for relative_path in excluded:
        assert not (REPO_ROOT / relative_path).exists()

    assert not (SOURCE_ROOT / "pilot_review.json").exists()
    assert not (SOURCE_ROOT / "human_review_gate.json").exists()
    assert not (SOURCE_ROOT / "human_review_response.json").exists()
    assert not (SOURCE_ROOT / "synthetic_human_review_panel.md").exists()


def test_imported_lessons_preserve_teacher_shape_and_non_claims() -> None:
    for case_id in REQUIRED_CASES:
        payload = json.loads(
            (SOURCE_ROOT / case_id / "mental_model_teacher_lesson.json").read_text(
                encoding="utf-8"
            )
        )
        lesson = payload["lesson"]
        non_claims = "\n".join(payload["non_claims"])

        assert payload["case_id"] == case_id
        assert payload["schema_version"] == "lolla.mental_model_teacher_lesson.v0"
        assert lesson["case_anchor"]
        assert lesson["dominant_thinking_move"]
        assert lesson["relationship_story"]
        assert lesson["model_stack"]
        assert lesson["practice_reps"]
        assert "does not prove the original answer was wrong" in lesson["do_not_overlearn"]
        assert "not decision correctness" in non_claims
        assert "does not authorize action" in non_claims


def test_imported_json_is_valid_and_private_marker_scan_is_clean() -> None:
    text_fragments = []

    for path in SOURCE_ROOT.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text_fragments.append(text)
        if path.suffix == ".json":
            json.loads(text)

    combined = "\n".join(text_fragments)
    for marker in PRIVATE_MARKERS:
        assert marker not in combined


def test_source_package_non_claims_and_stop_lines_are_visible() -> None:
    review = _review()
    doc = DOC.read_text(encoding="utf-8")
    combined = doc + "\n" + REVIEW.read_text(encoding="utf-8")

    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["runtime_integration_authorized"] is False
    assert "These imported files are source artifacts" in doc
    assert "They are not the product UI" in doc
    assert "product_proof\": true" not in combined
    assert "human_validated\": true" not in combined
    assert "runtime_integration_authorized\": true" not in combined


def test_readme_links_source_package_doc_and_markdown_links_resolve() -> None:
    index = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-three-case-source-package-v0.md" in index

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
