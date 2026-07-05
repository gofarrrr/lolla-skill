import json
import re
from pathlib import Path

from engine.system_b.mental_model_teacher_pilot_page_builder import build_pilot_page_data
from engine.system_b.mental_model_teacher_static_renderer import (
    RENDER_MANIFEST_SCHEMA_VERSION,
    render_pilot_pages,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RENDER_DIR = REPO_ROOT / "docs/product/mental-model-teacher-pilot-render-v0"
DOC = REPO_ROOT / "docs/product/mental-model-teacher-static-page-renderer-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-static-page-renderer-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"


def test_renderer_writes_temp_markdown_pages(tmp_path: Path) -> None:
    package = build_pilot_page_data(REPO_ROOT)
    manifest = render_pilot_pages(package, tmp_path)

    assert manifest["schema_version"] == RENDER_MANIFEST_SCHEMA_VERSION
    assert manifest["model_page_count"] == 3
    assert manifest["relation_page_count"] == 2
    assert (tmp_path / "index.md").exists()
    assert (tmp_path / "models/base-rates.md").exists()
    assert (tmp_path / "relations/base-rates__ally__system-2.md").exists()


def test_checked_in_render_manifest_matches_expected_pages() -> None:
    manifest = json.loads((RENDER_DIR / "manifest.json").read_text(encoding="utf-8"))
    paths = {page["path"] for page in manifest["pages"]}

    assert manifest["schema_version"] == RENDER_MANIFEST_SCHEMA_VERSION
    assert manifest["render_status"] == "pilot_render_ready_for_review"
    assert manifest["model_page_count"] == 3
    assert manifest["relation_page_count"] == 2
    assert {
        "index.md",
        "models/base-rates.md",
        "models/system-2.md",
        "models/scientific-method-evidence-testing.md",
        "relations/base-rates__ally__scientific-method-evidence-testing.md",
        "relations/base-rates__ally__system-2.md",
    } <= paths


def test_model_pages_have_required_readable_sections_and_no_json_dump() -> None:
    page = (RENDER_DIR / "models/base-rates.md").read_text(encoding="utf-8")

    for heading in [
        "# Base Rates",
        "## Helps Notice",
        "## Use When",
        "## Avoid When",
        "## Failure Modes",
        "## Premortem Questions",
        "## Heuristics",
        "## Common Misuse",
        "## Practice Prompts",
        "## Relations In This Pilot",
        "## Missingness",
        "## Source Custody",
        "## Non-Claims",
    ]:
        assert heading in page

    assert "schema_version" not in page
    assert "Missing in PR-P4 source-backed product fields." in page
    assert "`not_product_proof`" in page
    assert "`not_runtime_integration`" in page


def test_relation_page_story_precedes_taxonomy_and_links_models() -> None:
    page = (
        RENDER_DIR / "relations/base-rates__ally__system-2.md"
    ).read_text(encoding="utf-8")

    story_index = page.index("## Plain-Language Story")
    taxonomy_index = page.index("## Taxonomy And Source")
    assert story_index < taxonomy_index

    assert "[Base Rates](../models/base-rates.md)" in page
    assert "[System 2](../models/system-2.md)" in page
    assert "`relation_is_not_proof`" in page
    assert "`confidence_is_not_certification`" in page
    assert "not proof" in page


def test_rendered_markdown_local_links_resolve() -> None:
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


def test_rendered_pages_have_no_local_paths_or_runtime_claims() -> None:
    rendered = "\n".join(
        path.read_text(encoding="utf-8") for path in RENDER_DIR.rglob("*") if path.is_file()
    )

    assert "/" + "Users/" not in rendered
    assert "Desktop/" + "Apps" not in rendered
    assert "runtime integration authorized: true" not in rendered.lower()
    assert "product_proof`: `true" not in rendered
    assert "human_validated`: `true" not in rendered


def test_renderer_doc_and_review_preserve_pr_p5_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    index = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-static-page-renderer-v0.md" in index
    assert "mental-model-teacher-pilot-render-v0/index.md" in index
    assert review["decision_gate"] == "proceed_to_teacher_lesson_product_renderer"
    assert review["rendered_pages"]["model_pages"] == 3
    assert review["rendered_pages"]["relation_pages"] == 2

    for phrase in [
        "does not render Teacher lessons",
        "does not build graph data",
        "does not create graph UI",
        "does not call providers or model APIs",
        "does not wire runtime",
        "Teacher lesson page rendering",
        "graph UI",
    ]:
        assert phrase in doc
