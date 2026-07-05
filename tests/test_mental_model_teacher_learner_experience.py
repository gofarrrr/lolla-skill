import json
import re
from pathlib import Path
from typing import Any

from engine.system_b.mental_model_teacher_learner_experience import (
    LEARNER_EXPERIENCE_SCHEMA_VERSION,
    build_learner_experience_prototype,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/mental-model-teacher-learner-experience-prototype-v0.md"
SURFACE_DIR = REPO_ROOT / "docs/product/mental-model-teacher-learner-experience-prototype-v0"
HTML = SURFACE_DIR / "index.html"
MANIFEST = SURFACE_DIR / "manifest.json"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-learner-experience-prototype-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"
CASE_IDS = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _embedded_data(path: Path = HTML) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="learner-data" type="application/json">(.*?)</script>',
        text,
        re.DOTALL,
    )
    assert match is not None
    return json.loads(match.group(1))


def test_builder_writes_learner_experience_to_temp_dir(tmp_path: Path) -> None:
    manifest = build_learner_experience_prototype(REPO_ROOT, tmp_path)
    html = tmp_path / "index.html"
    generated_manifest = tmp_path / "manifest.json"
    data = _embedded_data(html)

    assert manifest["schema_version"] == LEARNER_EXPERIENCE_SCHEMA_VERSION
    assert manifest["status"] == "learner_first_static_prototype"
    assert manifest["entrypoint"] == "index.html"
    assert manifest["default_mode"] == "learn"
    assert manifest["embedded_data"] is True
    assert manifest["external_network_required"] is False
    assert manifest["provider_or_model_calls_used"] is False
    assert manifest["runtime_integration_authorized"] is False
    assert manifest["human_validated"] is False
    assert manifest["product_proof"] is False
    assert html.exists()
    assert generated_manifest.exists()
    assert data["schema_version"] == LEARNER_EXPERIENCE_SCHEMA_VERSION
    assert {case["case_id"] for case in data["cases"]} == CASE_IDS


def test_checked_in_manifest_records_learner_first_rules() -> None:
    manifest = _load_json(MANIFEST)

    assert manifest["schema_version"] == LEARNER_EXPERIENCE_SCHEMA_VERSION
    assert manifest["status"] == "learner_first_static_prototype"
    assert manifest["output_dir"] == (
        "docs/product/mental-model-teacher-learner-experience-prototype-v0"
    )
    assert manifest["default_mode"] == "learn"
    assert manifest["case_count"] == 3
    assert manifest["model_count"] == 9
    assert manifest["relation_count"] == 3
    assert manifest["mode_ids"] == ["learn", "models", "relations", "map", "review"]
    assert manifest["search_result_types"] == [
        "lesson",
        "model",
        "relation",
        "practice",
    ]
    assert manifest["learner_first_rules"] == {
        "learn_mode_default": True,
        "raw_source_snapshots_hidden_from_learn_mode": True,
        "review_controls_separate_from_learn_mode": True,
        "receipts_collapsed_by_default": True,
        "graph_is_secondary_map_mode": True,
        "typed_search_present": True,
        "model_backlinks_present": True,
        "relation_backlinks_present": True,
    }
    assert manifest["non_claims"]["product_proof"] is False
    assert manifest["non_claims"]["human_validated"] is False
    assert manifest["non_claims"]["runtime_integration_authorized"] is False


def test_html_defaults_to_learn_mode_and_keeps_review_separate() -> None:
    text = HTML.read_text(encoding="utf-8")
    data = _embedded_data()

    assert '<div id="app" class="app-shell"></div>' in text
    assert 'id="learner-data"' in text
    assert "fetch(" not in text
    assert "<script src=" not in text
    assert "<link rel=" not in text
    assert data["default_mode"] == "learn"
    assert [mode["id"] for mode in data["modes"]] == [
        "learn",
        "models",
        "relations",
        "map",
        "review",
    ]
    assert "Learn the move" in text
    assert "The trap" in text
    assert "Practice rep" in text
    assert "Models" in text
    assert "Relations" in text
    assert "Map" in text
    assert "Review" in text
    assert "Review mode" in text
    assert "Raw Teacher Comparison" not in text
    assert "Productized Lesson" not in text
    assert "GRAPH_REPORT" not in text


def test_embedded_data_has_typed_objects_search_and_backlinks() -> None:
    data = _embedded_data()

    assert len(data["cases"]) == 3
    assert len(data["models"]) == 9
    assert len(data["relations"]) == 3
    assert {item["type"] for item in data["search_index"]} == {
        "lesson",
        "model",
        "relation",
        "practice",
    }
    for case in data["cases"]:
        assert case["situation"]
        assert case["trap"]
        assert case["thinking_move"]
        assert case["relation"]["relation_type"] in {"ally", "antagonist", "tension"}
        assert len(case["model_stack"]) == 3
        assert len(case["graph"]["nodes"]) == 3
        assert len(case["graph"]["edges"]) == 1
        assert case["product_proof"] is False
        assert case["runtime_integration_authorized"] is False
        assert case["human_review_status"] == "pending"
    for model in data["models"]:
        assert model["appears_in"]
        assert model["href"].endswith(".md")
    for relation in data["relations"]:
        assert relation["used_in"]
        assert relation["href"].endswith(".md")
        assert relation["confidence"] == "medium"


def test_learner_experience_links_resolve() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    data = _embedded_data()
    for case in data["cases"]:
        for href in case["links"].values():
            if not (HTML.parent / href).resolve().exists():
                missing.append(href)
        for model in case["model_stack"]:
            if not (HTML.parent / model["href"]).resolve().exists():
                missing.append(model["href"])
        if not (HTML.parent / case["relation"]["href"]).resolve().exists():
            missing.append(case["relation"]["href"])
        for node in case["graph"]["nodes"]:
            if not (HTML.parent / node["href"]).resolve().exists():
                missing.append(node["href"])
        for edge in case["graph"]["edges"]:
            if not (HTML.parent / edge["href"]).resolve().exists():
                missing.append(edge["href"])

    for item in data["models"]:
        if not (HTML.parent / item["href"]).resolve().exists():
            missing.append(item["href"])
    for item in data["relations"]:
        if not (HTML.parent / item["href"]).resolve().exists():
            missing.append(item["href"])

    assert "mental-model-teacher-learner-experience-prototype-v0.md" in (
        README.read_text(encoding="utf-8")
    )
    assert "mental-model-teacher-learner-experience-prototype-v0/index.html" in (
        README.read_text(encoding="utf-8")
    )
    assert missing == []


def test_review_json_records_no_validation_or_proof_claims() -> None:
    review = _load_json(REVIEW)

    assert review["schema_version"] == (
        "lolla.mental_model_teacher.learner_experience_prototype_review.v0"
    )
    assert review["status"] == "learner_first_static_prototype_ready_for_review"
    assert review["prototype"]["default_mode"] == "learn"
    assert review["prototype"]["review_mode_separate"] is True
    assert review["prototype"]["typed_search"] is True
    assert review["prototype"]["backlinks_without_graph_required"] is True
    assert review["prototype"]["receipts_collapsed_by_default"] is True
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["runtime_integration_authorized"] is False


def test_learner_experience_artifacts_have_no_local_paths_or_positive_claims() -> None:
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
