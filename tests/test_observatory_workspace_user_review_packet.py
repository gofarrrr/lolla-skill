from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = REPO_ROOT / "docs/product/observatory-workspace-user-review-packet-v0"
DOC = REPO_ROOT / "docs/product/observatory-workspace-user-review-packet-v0.md"
INDEX = PACKET_DIR / "index.md"
FORM_MD = PACKET_DIR / "human-review-form.md"
FORM_JSON = PACKET_DIR / "human-review-form.json"
MANIFEST = PACKET_DIR / "manifest.json"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-user-review-packet-v0/review.json"
)
README = REPO_ROOT / "docs/product/README.md"

SURFACES = ["Outcome", "Learn", "Models", "Relations", "Map", "Receipts"]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_packet_doc_and_readme_index_the_review_packet() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    assert "Observatory Workspace User Review Packet" in readme
    assert "observatory-workspace-user-review-packet-v0.md" in readme
    assert "observatory-workspace-user-review-packet-v0/index.md" in readme
    assert "review packet and blank human review form" in doc
    assert "needs_human_review_before_observatory_expansion" in doc
    assert "Synthetic, automated, or Codex-assisted review remains diagnostic only" in doc
    assert "not human validation" in doc


def test_manifest_records_surfaces_ladder_and_closed_boundaries() -> None:
    manifest = _load_json(MANIFEST)

    assert manifest["schema_version"] == (
        "lolla.observatory_workspace_user_review_packet_manifest.v0"
    )
    assert manifest["status"] == (
        "observatory_workspace_user_review_packet_ready_for_human_review"
    )
    assert manifest["review_surfaces"] == SURFACES
    assert manifest["information_ladder"] == [
        "first_read",
        "optional_support",
        "drill_down_page",
        "receipts_or_audit",
    ]
    assert manifest["human_review_prefilled"] is False
    assert manifest["human_review_completed"] is False
    assert manifest["human_validated"] is False
    assert manifest["product_proof"] is False
    assert manifest["synthetic_review_diagnostic_only"] is True
    assert manifest["decision_gate"] == "needs_human_review_before_observatory_expansion"

    for ref in manifest["source_design_slices"]:
        assert (REPO_ROOT / ref).exists(), ref


def test_packet_asks_reviewers_to_judge_one_observatory_flow() -> None:
    index = INDEX.read_text(encoding="utf-8")
    normalized = " ".join(index.split())

    assert "Review the selected-run Observatory workspace as one product surface." in index
    assert "Do not create a new run for this review." in normalized
    assert "Do not run Lolla." in index
    assert "first read -> optional support -> drill-down page -> receipts/audit" in index
    assert "Outcome -> Learn -> Models -> Relations -> Map -> Receipts" in index
    assert "one product or several artifacts pasted together" in normalized
    assert "feel like a duplicate Teacher product outside Observatory" in index
    assert "A useful negative or partial review is a successful review outcome" in normalized

    for surface in SURFACES:
        assert f"### {surface}" in index
    for prompt in [
        "Does it avoid pretending the lesson proves the answer?",
        "Does the relation story come before technical labels?",
        "Does the map avoid implying graph edges are proof?",
        "Does Receipts keep Decision Work and technical audit separate from Learn?",
    ]:
        assert prompt in index
    assert "run outcome to one learnable reasoning move" in normalized


def test_human_review_markdown_form_is_blank_with_no_checked_defaults() -> None:
    form = FORM_MD.read_text(encoding="utf-8")

    assert "Status: blank form for human review." in form
    assert "[x]" not in form.lower()
    assert "[X]" not in form
    assert "Do not complete this form synthetically" in form
    assert "not human validation" in form

    for option in [
        "- [ ] ready to continue with caveats",
        "- [ ] needs first-screen revision",
        "- [ ] needs Learn revision",
        "- [ ] needs model/page revision",
        "- [ ] needs relation/page revision",
        "- [ ] needs graph/map UX revision",
        "- [ ] needs Receipts/audit revision",
        "- [ ] cannot judge from this packet",
    ]:
        assert option in form

    for surface in SURFACES:
        assert f"### {surface}" in form
    assert form.count("- [ ] strong") == 8
    assert form.count("- [ ] adequate") == 8
    assert form.count("- [ ] weak") == 8
    assert form.count("- [ ] cannot judge") >= 9


def test_human_review_json_form_preserves_blank_human_state() -> None:
    form = _load_json(FORM_JSON)

    assert form["schema_version"] == "lolla.observatory_workspace_human_review_form.v0"
    assert form["status"] == "blank_pending_human_review"
    assert form["prefilled_positive"] is False
    assert form["human_review_completed"] is False
    assert form["human_validated"] is False
    assert form["product_proof"] is False
    assert form["synthetic_review_diagnostic_only"] is True
    assert form["overall_decision"]["selected"] is None
    assert form["workspace_reviewed"]["case_id"] is None
    assert form["progression_review"]["selected"] is None
    assert form["progression_review"]["progression"] == SURFACES
    assert set(form["surface_reviews"].keys()) == set(SURFACES)

    for review in form["surface_reviews"].values():
        assert review["selected"] is None
        assert review["what_worked"] == ""
        assert review["what_should_change"] == ""

    assert form["information_hierarchy"]["selected"] is None
    assert form["non_claims_review"]["selected"] is None
    assert all(value is False for value in form["boundary_acknowledgement"].values())
    assert form["non_claims"]["product_proof"] is False
    assert form["non_claims"]["human_validated"] is False
    assert form["non_claims"]["answer_correctness"] is False
    assert form["non_claims"]["advice_correctness"] is False
    assert form["non_claims"]["runtime_integration_authorized"] is False
    assert form["non_claims"]["action_authorized"] is False


def test_review_json_records_packet_gate_without_runtime_or_validation_claims() -> None:
    review = _load_json(REVIEW)

    assert review["decision_gate"] == "needs_human_review_before_observatory_expansion"
    assert review["implemented"]["review_packet"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert review["review_packet"]["surfaces"] == SURFACES
    assert review["human_form"]["prefilled_positive"] is False
    assert review["human_form"]["human_review_completed"] is False
    assert review["human_form"]["human_validated"] is False
    assert review["human_form"]["product_proof"] is False
    assert review["human_form"]["boundary_acknowledgements_checked"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


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
    for artifact in [
        manifest["packet"],
        manifest["human_review_form_markdown"],
        manifest["human_review_form_json"],
    ]:
        if not (PACKET_DIR / artifact).exists():
            missing.append(artifact)

    assert missing == []


def test_packet_artifacts_have_no_local_paths_or_positive_claims() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [DOC, INDEX, FORM_MD, FORM_JSON, MANIFEST, REVIEW]
    )

    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
