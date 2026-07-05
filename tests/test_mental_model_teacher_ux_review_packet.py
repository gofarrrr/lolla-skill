import json
import re
from pathlib import Path

from engine.system_b.mental_model_teacher_ux_review_packet import (
    HUMAN_REVIEW_FORM_SCHEMA_VERSION,
    REVIEW_CRITERIA,
    UX_REVIEW_PACKET_MANIFEST_SCHEMA_VERSION,
    build_ux_review_packet,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = REPO_ROOT / "docs/product/mental-model-teacher-ux-review-packet-v0"
DOC = REPO_ROOT / "docs/product/mental-model-teacher-ux-review-packet-v0.md"
INDEX = PACKET_DIR / "index.md"
FORM_MD = PACKET_DIR / "human-review-form.md"
FORM_JSON = PACKET_DIR / "human-review-form.json"
MANIFEST = PACKET_DIR / "manifest.json"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/mental-model-teacher-ux-review-packet-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"

CASE_IDS = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_builder_writes_blank_ux_review_packet_to_temp_dir(tmp_path: Path) -> None:
    manifest = build_ux_review_packet(REPO_ROOT, tmp_path)

    assert manifest["schema_version"] == UX_REVIEW_PACKET_MANIFEST_SCHEMA_VERSION
    assert manifest["status"] == "ux_review_packet_ready_for_human_review"
    assert manifest["case_count"] == 3
    assert manifest["criteria"] == list(REVIEW_CRITERIA)
    assert manifest["human_review_prefilled"] is False
    assert manifest["human_review_completed"] is False
    assert manifest["human_validated"] is False
    assert manifest["product_proof"] is False
    assert manifest["runtime_integration_authorized"] is False
    assert manifest["synthetic_review_diagnostic_only"] is True

    assert (tmp_path / "index.md").exists()
    assert (tmp_path / "human-review-form.md").exists()
    assert (tmp_path / "human-review-form.json").exists()
    assert (tmp_path / "manifest.json").exists()

    form = _load_json(tmp_path / "human-review-form.json")
    assert form["schema_version"] == HUMAN_REVIEW_FORM_SCHEMA_VERSION
    assert form["status"] == "blank_pending_human_review"
    assert form["overall_decision"]["selected"] is None


def test_checked_in_manifest_points_to_three_reviewable_cases_and_artifacts() -> None:
    manifest = _load_json(MANIFEST)

    assert manifest["schema_version"] == UX_REVIEW_PACKET_MANIFEST_SCHEMA_VERSION
    assert manifest["status"] == "ux_review_packet_ready_for_human_review"
    assert manifest["source_pilot_manifest"] == (
        "docs/product/mental-model-teacher-three-case-product-pilot-v0/manifest.json"
    )
    assert manifest["case_count"] == 3
    assert {item["case_id"] for item in manifest["case_artifacts"]} == CASE_IDS
    assert manifest["packet"] == "index.md"
    assert manifest["human_review_form_markdown"] == "human-review-form.md"
    assert manifest["human_review_form_json"] == "human-review-form.json"

    for case in manifest["case_artifacts"]:
        for artifact in case.values():
            if artifact in CASE_IDS:
                continue
            assert (REPO_ROOT / artifact).exists(), artifact


def test_review_packet_compares_expected_surfaces_without_decision_work_collapse() -> None:
    index = INDEX.read_text(encoding="utf-8")
    normalized_index = " ".join(index.split())

    for criterion in REVIEW_CRITERIA:
        assert f"`{criterion}`" in index
    for case_id in CASE_IDS:
        assert f"`{case_id}`" in index

    for label in [
        "Product lesson",
        "Teacher card",
        "Teacher note",
        "Relation page",
        "Graph neighborhood",
        "Decision Work boundary reference",
    ]:
        assert label in index

    assert "not decision correctness" in index
    assert "comparison artifacts, not product pages" in index
    assert "not full product relation pages" in index
    assert "not proof of relation truth" in index
    assert "Decision Work briefs are boundary references only" in index
    assert (
        "Teacher asks what reasoning move can be learned"
        in normalized_index
    )


def test_human_review_markdown_form_is_blank_and_has_no_positive_defaults() -> None:
    form = FORM_MD.read_text(encoding="utf-8")

    assert "Status: blank form for human review." in form
    assert "no positive defaults" not in form.lower()
    assert "[x]" not in form.lower()
    assert "[X]" not in form
    assert "Do not complete this form synthetically" in form
    assert "not human validation" in form

    for option in [
        "- [ ] ready to package with caveats",
        "- [ ] needs model/page revision",
        "- [ ] needs relation/page revision",
        "- [ ] needs graph UX revision",
        "- [ ] needs human review before expansion",
        "- [ ] cannot judge from this packet",
    ]:
        assert option in form

    for case_id in CASE_IDS:
        assert f"## Case: `{case_id}`" in form
    for criterion in REVIEW_CRITERIA:
        assert form.count(f"### `{criterion}`") == 3
    assert form.count("- [ ] strong") == 18
    assert form.count("- [ ] adequate") == 18
    assert form.count("- [ ] weak") == 18
    assert form.count("- [ ] cannot judge") >= 21


def test_human_review_json_form_preserves_blank_human_state() -> None:
    form = _load_json(FORM_JSON)

    assert form["schema_version"] == HUMAN_REVIEW_FORM_SCHEMA_VERSION
    assert form["status"] == "blank_pending_human_review"
    assert form["prefilled_positive"] is False
    assert form["human_review_completed"] is False
    assert form["human_validated"] is False
    assert form["product_proof"] is False
    assert form["synthetic_review_diagnostic_only"] is True
    assert form["overall_decision"]["selected"] is None
    assert form["overall_decision"]["notes"] == ""
    assert {case["case_id"] for case in form["cases"]} == CASE_IDS

    for case in form["cases"]:
        assert case["case_decision"]["selected"] is None
        assert case["case_decision"]["notes"] == ""
        assert case["criteria"].keys() == set(REVIEW_CRITERIA)
        for criterion in case["criteria"].values():
            assert criterion["selected"] is None
            assert criterion["evidence"] == ""
            assert criterion["notes"] == ""

    assert all(value is False for value in form["boundary_acknowledgement"].values())
    assert form["non_claims"]["product_proof"] is False
    assert form["non_claims"]["human_validated"] is False
    assert form["non_claims"]["answer_correctness"] is False
    assert form["non_claims"]["advice_correctness"] is False
    assert form["non_claims"]["runtime_integration_authorized"] is False
    assert form["non_claims"]["graph_edges_are_proof"] is False


def test_markdown_links_and_json_artifact_paths_resolve() -> None:
    missing = []
    for path in [DOC, INDEX, FORM_MD, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    manifest = _load_json(MANIFEST)
    form = _load_json(FORM_JSON)
    for artifact in [
        manifest["source_pilot_manifest"],
        *(
            value
            for case in manifest["case_artifacts"]
            for key, value in case.items()
            if key != "case_id"
        ),
        *(
            value
            for case in form["cases"]
            for value in case["artifacts"].values()
        ),
    ]:
        if not (REPO_ROOT / artifact).exists():
            missing.append(artifact)

    assert missing == []


def test_review_json_records_pr_p10_gate_and_no_prefilled_human_validation() -> None:
    review = _load_json(REVIEW)
    readme = README.read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    normalized_doc = " ".join(doc.split())

    assert "mental-model-teacher-ux-review-packet-v0.md" in readme
    assert "mental-model-teacher-ux-review-packet-v0/index.md" in readme
    assert review["decision_gate"] == "needs_human_review_before_expansion"
    assert review["review_packet"]["case_count"] == 3
    assert review["human_form"]["prefilled_positive"] is False
    assert review["human_form"]["human_review_completed"] is False
    assert review["human_form"]["human_validated"] is False
    assert review["human_form"]["product_proof"] is False
    assert review["comparison_inputs"]["productized_teacher_pages"] is True
    assert review["comparison_inputs"]["current_teacher_cards_and_notes"] is True
    assert review["comparison_inputs"]["relation_source_views"] is True
    assert review["comparison_inputs"]["graph_neighborhood_json"] is True
    assert review["comparison_inputs"]["decision_work_boundary_references"] is True
    assert review["comparison_inputs"]["decision_work_used_as_teacher_source"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["runtime_integration_authorized"] is False

    for phrase in [
        "current Teacher cards and notes",
        "Decision Work briefs as boundary references only",
        "no positive defaults",
        "not human validation",
        "PR-P10 stops before",
    ]:
        assert phrase in normalized_doc


def test_packet_has_no_local_paths_or_positive_claims() -> None:
    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            DOC,
            INDEX,
            FORM_MD,
            FORM_JSON,
            MANIFEST,
            REVIEW,
        ]
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
    assert "\"embedding_similarity\":" not in rendered
    assert "\"affinity\"" not in rendered
    assert "\"rank\"" not in rendered
    assert "\"score\"" not in rendered
