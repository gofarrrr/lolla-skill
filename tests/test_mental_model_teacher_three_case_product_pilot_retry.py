import json
import re
from pathlib import Path

from engine.system_b.mental_model_teacher_product_contracts import (
    validate_teacher_lesson,
    validate_visual_graph,
)
from engine.system_b.mental_model_teacher_three_case_product_pilot import (
    CASE_IDS,
    THREE_CASE_PRODUCT_PILOT_MANIFEST_SCHEMA_VERSION,
    build_three_case_product_pilot,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PILOT_DIR = REPO_ROOT / "docs/product/mental-model-teacher-three-case-product-pilot-v0"
MANIFEST = PILOT_DIR / "manifest.json"
DOC = REPO_ROOT / "docs/product/mental-model-teacher-three-case-product-pilot-retry-v0.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-three-case-product-pilot-retry-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_builder_writes_three_case_product_pilot_to_temp_dir(tmp_path: Path) -> None:
    manifest = build_three_case_product_pilot(REPO_ROOT, tmp_path)

    assert manifest["schema_version"] == THREE_CASE_PRODUCT_PILOT_MANIFEST_SCHEMA_VERSION
    assert manifest["case_count"] == 3
    assert manifest["lesson_page_count"] == 3
    assert manifest["graph_count"] == 3
    assert manifest["source_artifacts_used"] is True
    assert manifest["decision_work_artifacts_used_as_teacher_source"] is False
    assert manifest["provider_or_model_calls_used"] is False
    assert manifest["runtime_integration_authorized"] is False
    assert (tmp_path / "index.md").exists()
    for case_id in CASE_IDS:
        assert (tmp_path / "lessons" / f"{case_id}.md").exists()
        assert (tmp_path / "objects" / f"{case_id}.lesson.json").exists()
        assert (tmp_path / "graphs" / f"{case_id}.graph.json").exists()


def test_checked_in_manifest_records_three_real_teacher_cases() -> None:
    manifest = _load_json(MANIFEST)

    assert manifest["schema_version"] == THREE_CASE_PRODUCT_PILOT_MANIFEST_SCHEMA_VERSION
    assert manifest["status"] == "three_case_teacher_product_pilot_ready_for_review"
    assert manifest["case_count"] == 3
    assert manifest["lesson_object_count"] == 3
    assert manifest["lesson_page_count"] == 3
    assert manifest["graph_count"] == 3
    assert manifest["source_root"] == (
        "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2"
    )
    assert manifest["product_proof"] is False
    assert manifest["human_validated"] is False
    assert manifest["runtime_integration_authorized"] is False
    assert set(manifest["high_risk_cases"]) == {"ceo-remove-founding-cofounder"}


def test_lesson_objects_validate_and_preserve_source_custody() -> None:
    for case_id in CASE_IDS:
        path = PILOT_DIR / "objects" / f"{case_id}.lesson.json"
        lesson = validate_teacher_lesson(_load_json(path))

        assert lesson["case_id"] == case_id
        assert lesson["lesson_id"] == case_id
        assert lesson["human_review_status"] == "pending"
        assert lesson["product_proof"] is False
        assert lesson["runtime_integration_authorized"] is False
        assert lesson["missingness"]["status"] == "partial"
        assert "full_model_product_pages" in lesson["missingness"]["missing_fields"]
        assert "full_relation_product_pages" in lesson["missingness"]["missing_fields"]
        assert len(lesson["model_stack"]) == 3
        assert len(lesson["model_links"]) == 3
        assert len(lesson["relation_links"]) == 1
        assert all(
            ref["path"].startswith(
                f"reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2/{case_id}/"
            )
            for ref in lesson["source_refs"]
        )


def test_lesson_pages_render_required_product_sections_and_non_claims() -> None:
    required_headings = [
        "## Case Anchor",
        "## Thinking Move",
        "## Why This Move Mattered",
        "## Model Stack",
        "## Relation Story",
        "## Relation Clickthrough",
        "## Worked Example",
        "## Practice Rep",
        "## Do Not Overlearn",
        "## Human Gate Status",
        "## Source Trail",
        "## Graph Neighborhood",
        "## Non-Claims",
    ]

    for case_id in CASE_IDS:
        page = (PILOT_DIR / "lessons" / f"{case_id}.md").read_text(encoding="utf-8")
        for heading in required_headings:
            assert heading in page
        assert "case is the anchor" in page
        assert "reasoning move is the subject" in page
        assert "model relationship is the lesson" in page
        assert "practice rep is the product value" in page
        assert "Human review status: `pending`" in page
        assert "Product proof: `false`" in page
        assert "Runtime integration authorized: `false`" in page
        assert "`not_product_proof`" in page
        assert "`not_human_validation`" in page
        assert "`not_answer_correctness`" in page
        assert "`not_advice_correctness`" in page
        assert "`not_runtime_integration`" in page
        assert "`not_action_authorization`" in page


def test_high_risk_ceo_case_keeps_domain_caveat_visible() -> None:
    page = (
        PILOT_DIR / "lessons/ceo-remove-founding-cofounder.md"
    ).read_text(encoding="utf-8")

    assert "## High-Risk Case Caveat" in page
    assert "legal answer" in page
    assert "HR answer" in page
    assert "governance answer" in page
    assert "interpersonal answer" in page
    assert "advice correctness" in page
    assert "answer correctness" in page


def test_graph_objects_validate_and_keep_edges_as_navigation_not_proof() -> None:
    expected_relation_types = {
        "launch-public-enterprise-beta": "antagonist",
        "deploy-assisted-intake-routing": "tension",
        "ceo-remove-founding-cofounder": "ally",
    }

    for case_id, relation_type in expected_relation_types.items():
        graph = validate_visual_graph(
            _load_json(PILOT_DIR / "graphs" / f"{case_id}.graph.json")
        )

        assert graph["case_id"] == case_id
        assert graph["graph_scope"] == "lesson_neighborhood"
        assert len(graph["nodes"]) == 3
        assert len(graph["edges"]) == 1
        assert graph["edges"][0]["relation_type"] == relation_type
        assert graph["edges"][0]["confidence"] == "medium"
        assert "edge_is_not_proof" in graph["non_claims"]
        assert "graph_is_navigation_not_proof" in graph["non_claims"]
        for forbidden_key in ("affinity", "rank", "embedding_similarity", "score"):
            assert forbidden_key not in graph["edges"][0]


def test_markdown_and_graph_links_resolve() -> None:
    markdown_files = list(PILOT_DIR.rglob("*.md")) + [DOC, README]
    missing = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    for graph_path in (PILOT_DIR / "graphs").glob("*.graph.json"):
        graph = _load_json(graph_path)
        for node in graph["nodes"]:
            if not (graph_path.parent / node["href"]).resolve().exists():
                missing.append(f"{graph_path}: {node['href']}")
        for edge in graph["edges"]:
            if not (graph_path.parent / edge["href"]).resolve().exists():
                missing.append(f"{graph_path}: {edge['href']}")

    assert missing == []


def test_review_and_docs_preserve_pr_p9_retry_boundaries() -> None:
    review = _load_json(REVIEW)
    doc = DOC.read_text(encoding="utf-8")
    normalized_doc = " ".join(doc.split())
    index = README.read_text(encoding="utf-8")

    assert "mental-model-teacher-three-case-product-pilot-retry-v0.md" in index
    assert "mental-model-teacher-three-case-product-pilot-v0/index.md" in index
    assert review["decision_gate"] == "proceed_to_ux_review_packet"
    assert review["product_pilot"]["case_count"] == 3
    assert review["product_pilot"]["lesson_page_count"] == 3
    assert review["product_pilot"]["graph_count"] == 3
    assert review["source_package"]["teacher_source_artifacts_used"] is True
    assert review["source_package"]["decision_work_artifacts_used_as_teacher_source"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["runtime_integration_authorized"] is False

    for phrase in [
        "does not use Decision Work artifacts as Teacher source",
        "does not call providers or model APIs",
        "does not create a new Lolla run",
        "does not wire runtime behavior",
        "Graph edges are navigation and teaching context only",
        "stops before",
    ]:
        assert phrase in normalized_doc


def test_rendered_package_has_no_local_paths_or_positive_claims() -> None:
    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            *PILOT_DIR.rglob("*"),
            DOC,
            REVIEW,
        ]
        if path.is_file()
    )

    assert "/" + "Users/" not in rendered
    assert "Desktop/" + "Apps" not in rendered
    assert "product_proof\": true" not in rendered
    assert "human_validated\": true" not in rendered
    assert "runtime_integration_authorized\": true" not in rendered
    assert "Product proof: `true`" not in rendered
    assert "Runtime integration authorized: `true`" not in rendered
    assert "\"embedding_similarity\":" not in rendered
    assert "\"affinity\"" not in rendered
    assert "\"rank\"" not in rendered
    assert "\"score\"" not in rendered
