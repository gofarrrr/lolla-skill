import json
import re
from pathlib import Path
from typing import Any

from engine.system_b.mental_model_teacher_visible_review_surface import (
    VISIBLE_SURFACE_SCHEMA_VERSION,
    build_visible_review_surface,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SURFACE_DIR = REPO_ROOT / "docs/product/mental-model-teacher-visible-review-surface-v0"
DOC = REPO_ROOT / "docs/product/mental-model-teacher-visible-review-surface-v0.md"
HTML = SURFACE_DIR / "index.html"
MANIFEST = SURFACE_DIR / "manifest.json"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-visible-review-surface-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"
CASE_IDS = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _embedded_surface_data() -> dict[str, Any]:
    text = HTML.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="surface-data" type="application/json">(.*?)</script>',
        text,
        re.DOTALL,
    )
    assert match is not None
    return json.loads(match.group(1))


def test_builder_writes_visible_review_surface_to_temp_dir(tmp_path: Path) -> None:
    manifest = build_visible_review_surface(REPO_ROOT, tmp_path)

    assert manifest["schema_version"] == VISIBLE_SURFACE_SCHEMA_VERSION
    assert manifest["status"] == "visible_review_surface_ready_for_human_review"
    assert manifest["case_count"] == 3
    assert manifest["entrypoint"] == "index.html"
    assert manifest["embedded_data"] is True
    assert manifest["external_network_required"] is False
    assert manifest["provider_or_model_calls_used"] is False
    assert manifest["runtime_integration_authorized"] is False
    assert manifest["human_review_completed"] is False
    assert manifest["human_validated"] is False
    assert manifest["product_proof"] is False
    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "manifest.json").exists()


def test_checked_in_manifest_records_visible_static_surface() -> None:
    manifest = _load_json(MANIFEST)

    assert manifest["schema_version"] == VISIBLE_SURFACE_SCHEMA_VERSION
    assert manifest["status"] == "visible_review_surface_ready_for_human_review"
    assert manifest["output_dir"] == "docs/product/mental-model-teacher-visible-review-surface-v0"
    assert manifest["entrypoint"] == "index.html"
    assert manifest["case_count"] == 3
    assert manifest["decision_gate"] == "needs_human_review_before_expansion"
    assert manifest["embedded_data"] is True
    assert manifest["external_network_required"] is False
    assert manifest["provider_or_model_calls_used"] is False
    assert manifest["runtime_integration_authorized"] is False
    assert manifest["human_review_completed"] is False
    assert manifest["human_validated"] is False
    assert manifest["product_proof"] is False
    assert {item["case_id"] for item in manifest["case_artifacts"]} == CASE_IDS


def test_html_embeds_three_case_product_data_and_review_controls() -> None:
    text = HTML.read_text(encoding="utf-8")
    data = _embedded_surface_data()

    assert '<div id="app" class="app-shell"></div>' in text
    assert "fetch(" not in text
    assert "<script src=" not in text
    assert "<link rel=" not in text
    assert data["schema_version"] == VISIBLE_SURFACE_SCHEMA_VERSION
    assert data["decision_gate"] == "needs_human_review_before_expansion"
    assert {case["case_id"] for case in data["cases"]} == CASE_IDS
    assert len(data["review_criteria"]) == 6
    for case in data["cases"]:
        assert case["case_title"]
        assert case["case_anchor"]
        assert case["thinking_move"]
        assert case["relation_story"]
        assert len(case["model_stack"]) == 3
        assert len(case["graph"]["nodes"]) == 3
        assert len(case["graph"]["edges"]) == 1
        assert case["source_snapshots"]["card"]["thinking_move"]
        assert case["source_snapshots"]["note"]["case_anchor"]
    for ui_phrase in [
        "Mental Model Teacher Pilot",
        "Productized Lesson",
        "Model Stack",
        "Lesson Graph",
        "Raw Teacher Comparison",
        "Human Review",
        "Non-Claims",
        "strong",
        "adequate",
        "weak",
        "cannot judge",
    ]:
        assert ui_phrase in text


def test_html_data_preserves_non_claims_and_blank_review_state() -> None:
    data = _embedded_surface_data()

    assert data["non_claims"]["product_proof"] is False
    assert data["non_claims"]["human_validated"] is False
    assert data["non_claims"]["answer_correctness"] is False
    assert data["non_claims"]["advice_correctness"] is False
    assert data["non_claims"]["runtime_integration_authorized"] is False
    assert data["non_claims"]["graph_edges_are_proof"] is False
    assert data["non_claims"]["agent_or_automatic_action_authorized"] is False
    for case in data["cases"]:
        assert case["human_review_status"] == "pending"
        assert case["product_proof"] is False
        assert case["runtime_integration_authorized"] is False
        assert "not_product_proof" in case["non_claims"]
        assert "not_human_validation" in case["non_claims"]
        assert "not_answer_correctness" in case["non_claims"]
        assert "not_advice_correctness" in case["non_claims"]


def test_visible_surface_links_resolve() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    manifest = _load_json(MANIFEST)
    for item in manifest["case_artifacts"]:
        for key, ref in item.items():
            if key != "case_id" and not (REPO_ROOT / ref).exists():
                missing.append(ref)

    data = _embedded_surface_data()
    for case in data["cases"]:
        for href in case["artifact_links"].values():
            if not (HTML.parent / href).resolve().exists():
                missing.append(href)
        for node in case["graph"]["nodes"]:
            if not (HTML.parent / node["href"]).resolve().exists():
                missing.append(node["href"])
        for edge in case["graph"]["edges"]:
            if not (HTML.parent / edge["href"]).resolve().exists():
                missing.append(edge["href"])

    assert "mental-model-teacher-visible-review-surface-v0.md" in (
        README.read_text(encoding="utf-8")
    )
    assert "mental-model-teacher-visible-review-surface-v0/index.html" in (
        README.read_text(encoding="utf-8")
    )
    assert missing == []


def test_review_json_records_visible_surface_without_validation_claims() -> None:
    review = _load_json(REVIEW)

    assert review["schema_version"] == (
        "lolla.mental_model_teacher.visible_review_surface_review.v0"
    )
    assert review["status"] == "visible_review_surface_ready_for_human_review"
    assert review["decision_gate"] == "needs_human_review_before_expansion"
    assert review["case_count"] == 3
    assert review["visible_surface"]["browser_visible"] is True
    assert review["visible_surface"]["static_html"] is True
    assert review["visible_surface"]["embedded_data"] is True
    assert review["visible_surface"]["external_network_required"] is False
    assert review["visible_surface"]["review_controls_blank"] is True
    assert review["visible_surface"]["graph_neighborhood_visible"] is True
    assert review["visible_surface"]["raw_teacher_snapshots_visible"] is True
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["runtime_integration_authorized"] is False


def test_visible_surface_artifacts_have_no_local_paths_or_positive_claims() -> None:
    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [DOC, HTML, MANIFEST, REVIEW]
    )

    assert "/" + "Users/" not in rendered
    assert "Desktop/" + "Apps" not in rendered
    assert "product_proof\": true" not in rendered
    assert "human_validated\": true" not in rendered
    assert "human_review_completed\": true" not in rendered
    assert "runtime_integration_authorized\": true" not in rendered
    assert "answer_correctness\": true" not in rendered
    assert "advice_correctness\": true" not in rendered
    assert "Product proof: `true`" not in rendered
    assert "Runtime integration authorized: `true`" not in rendered
