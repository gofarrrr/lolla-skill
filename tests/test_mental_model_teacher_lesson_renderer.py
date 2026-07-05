import json
import re
from pathlib import Path

from engine.system_b.mental_model_teacher_lesson_renderer import (
    LESSON_RENDER_MANIFEST_SCHEMA_VERSION,
    load_contract_fixture_lesson,
    render_lesson_pages,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = REPO_ROOT / "docs/product/mental-model-teacher-lesson-render-v0"
LESSON_PAGE = (
    RENDER_DIR / "lessons/contract-fixture-base-rates-system-2.md"
)
DOC = REPO_ROOT / "docs/product/mental-model-teacher-lesson-product-renderer-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-lesson-product-renderer-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"


def test_renderer_writes_temp_lesson_markdown(tmp_path: Path) -> None:
    lesson = load_contract_fixture_lesson(REPO_ROOT)
    manifest = render_lesson_pages([lesson], tmp_path)

    assert manifest["schema_version"] == LESSON_RENDER_MANIFEST_SCHEMA_VERSION
    assert manifest["lesson_count"] == 1
    assert manifest["teacher_artifacts_used"] is False
    assert manifest["real_teacher_case_claimed"] is False
    assert (tmp_path / "index.md").exists()
    assert (tmp_path / "lessons/contract-fixture-base-rates-system-2.md").exists()


def test_checked_in_lesson_render_manifest_matches_expected_page() -> None:
    manifest = json.loads((RENDER_DIR / "manifest.json").read_text(encoding="utf-8"))
    paths = {page["path"] for page in manifest["pages"]}

    assert manifest["schema_version"] == LESSON_RENDER_MANIFEST_SCHEMA_VERSION
    assert manifest["render_status"] == "fixture_lesson_render_ready_for_review"
    assert manifest["lesson_count"] == 1
    assert manifest["teacher_artifacts_used"] is False
    assert manifest["real_teacher_case_claimed"] is False
    assert manifest["non_claims"]["product_proof"] is False
    assert manifest["non_claims"]["human_validated"] is False
    assert manifest["non_claims"]["runtime_integration_authorized"] is False
    assert manifest["non_claims"]["agent_or_automatic_action_authorized"] is False
    assert manifest["non_claims"]["real_teacher_case_artifact_claimed"] is False
    assert {
        "index.md",
        "lessons/contract-fixture-base-rates-system-2.md",
    } <= paths


def test_lesson_page_has_required_teacher_sections_and_framing() -> None:
    page = LESSON_PAGE.read_text(encoding="utf-8")

    for heading in [
        "## Case Anchor",
        "## Thinking Move",
        "## Model Stack",
        "## Relation Story",
        "## Model Clickthroughs",
        "## Relation Clickthroughs",
        "## Worked Example",
        "## Practice Rep",
        "## Do Not Overlearn",
        "## Human Gate Status",
        "## Missingness",
        "## Source Refs",
        "## Non-Claims",
    ]:
        assert heading in page

    assert "case is the anchor" in page
    assert "reasoning move is the subject" in page
    assert "model relationship is the lesson" in page
    assert "practice rep is the product value" in page
    assert "It is not a completed real Teacher case artifact." in page


def test_lesson_page_links_to_model_and_relation_pages() -> None:
    page = LESSON_PAGE.read_text(encoding="utf-8")

    assert (
        "../../mental-model-teacher-pilot-render-v0/models/base-rates.md"
    ) in page
    assert (
        "../../mental-model-teacher-pilot-render-v0/models/system-2.md"
    ) in page
    assert (
        "../../mental-model-teacher-pilot-render-v0/relations/base-rates__ally__system-2.md"
    ) in page


def test_lesson_page_keeps_gate_status_and_non_claims_visible() -> None:
    page = LESSON_PAGE.read_text(encoding="utf-8")

    assert "Human review status: `not_reviewed`" in page
    assert "Product proof: `false`" in page
    assert "Runtime integration authorized: `false`" in page
    assert "`not_product_proof`" in page
    assert "`not_human_validation`" in page
    assert "`not_answer_correctness`" in page
    assert "`not_advice_correctness`" in page
    assert "`not_runtime_integration`" in page
    assert "`not_action_authorization`" in page
    assert "`lesson_is_not_advice`" in page
    assert "`practice_is_not_validation`" in page
    assert "`real_case_artifact`" in page


def test_lesson_rendered_markdown_local_links_resolve() -> None:
    markdown_files = list(RENDER_DIR.rglob("*.md")) + [DOC, README]
    missing = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    assert missing == []


def test_lesson_pages_have_no_local_paths_or_runtime_claims() -> None:
    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in RENDER_DIR.rglob("*")
        if path.is_file()
    )

    assert "/" + "Users/" not in rendered
    assert "Desktop/" + "Apps" not in rendered
    assert "runtime integration authorized: `true`" not in rendered.lower()
    assert "product proof: `true`" not in rendered.lower()
    assert "human_validated\": true" not in rendered
    assert "Decision Work" not in LESSON_PAGE.read_text(encoding="utf-8")
    assert "telemetry" not in LESSON_PAGE.read_text(encoding="utf-8").lower()


def test_renderer_doc_and_review_preserve_pr_p6_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    index = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-lesson-product-renderer-v0.md" in index
    assert "mental-model-teacher-lesson-render-v0/index.md" in index
    assert review["decision_gate"] == "proceed_to_lesson_neighborhood_graph_data_builder"
    assert review["rendered_pages"]["teacher_lesson_pages"] == 1
    assert review["input_status"]["real_teacher_case_artifacts_present"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["runtime_integration_authorized"] is False

    for phrase in [
        "does not read or create real Teacher case artifacts",
        "does not build graph data",
        "does not create graph UI",
        "does not call providers or model APIs",
        "does not wire runtime",
        "graph data building",
        "browser graph UI",
    ]:
        assert phrase in doc
