from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

from engine.system_b.observatory_workspace_human_review_intake import (  # noqa: E402
    FOCUSED_HIERARCHY_CHECKS,
    SURFACES,
    validate_observatory_workspace_human_review_form,
)
import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-workspace-human-hierarchy-scorecard-v0.md"
README = REPO_ROOT / "docs/product/README.md"
FORM_MD = (
    REPO_ROOT
    / "docs/product/observatory-workspace-user-review-packet-v0/human-review-form.md"
)
FORM_JSON = (
    REPO_ROOT
    / "docs/product/observatory-workspace-user-review-packet-v0/human-review-form.json"
)
MANIFEST = (
    REPO_ROOT / "docs/product/observatory-workspace-user-review-packet-v0/manifest.json"
)
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-human-hierarchy-scorecard-v0/review.json"
)


def _install_launch_case(monkeypatch) -> None:
    monkeypatch.setattr(
        serve_result,
        "_RESULT",
        {
            "usage_summary": {"run_id": "20260627T104146Z_7bfe79"},
            "extraction": {
                "decision_situation": (
                    "A public enterprise beta launch is being reviewed."
                )
            },
            "run_health": {"overall": "healthy", "issues": []},
            "revised_answer": (
                "Launch in stages after the support risk is made explicit. "
                "Keep the first cohort narrow and treat the beta as a learning gate."
            ),
        },
    )
    monkeypatch.setattr(serve_result, "_RESULT_PATH", None)
    monkeypatch.setattr(serve_result, "_CASE_ID", "lolla-audit")
    monkeypatch.setattr(serve_result, "_CASE_NAME", "Lolla Audit")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _completed_form() -> dict:
    form = copy.deepcopy(_load_json(FORM_JSON))
    form["status"] = "completed_human_review"
    form["human_review_completed"] = True
    form["workspace_reviewed"] = {
        "case_id": "lolla-audit",
        "run_id": "20260627T104146Z_7bfe79",
        "review_date": "2026-07-07",
        "reviewer": "human-reviewer",
    }
    form["overall_decision"]["selected"] = "ready_to_continue_with_caveats"
    form["overall_decision"]["notes"] = "Focused hierarchy review completed."
    form["first_impression"] = {
        "page_purpose_in_first_ten_seconds": "A run learning workspace.",
        "wanted_next_click": "Outcome, then Learn.",
        "one_product_or_artifact_pile": "Mostly one product.",
    }
    form["progression_review"]["selected"] = "adequate"
    form["progression_review"]["evidence"] = (
        "The workspace has a recognizable sequence."
    )
    for surface in SURFACES:
        form["surface_reviews"][surface]["selected"] = "adequate"
        form["surface_reviews"][surface]["what_worked"] = (
            f"{surface} has a clear job."
        )
        form["surface_reviews"][surface]["what_should_change"] = ""
    for check in FOCUSED_HIERARCHY_CHECKS:
        form["focused_hierarchy_checks"][check]["selected"] = "adequate"
        form["focused_hierarchy_checks"][check]["evidence"] = (
            f"{check} was reviewed."
        )
    form["information_hierarchy"]["selected"] = "adequate"
    form["information_hierarchy"]["evidence"] = (
        "The first read and drilldown layers are distinguishable."
    )
    form["non_claims_review"]["selected"] = "yes"
    form["non_claims_review"]["evidence"] = "The page avoids proof claims."
    return form


def test_review_guide_exposes_focused_hierarchy_scorecard(monkeypatch) -> None:
    _install_launch_case(monkeypatch)

    html = serve_result._render_workspace_review_guide_html("lolla-audit")

    assert "Focused hierarchy scorecard" in html
    assert "Check the six places where the product can collapse into artifacts." in html
    for phrase in [
        "First screen: can you say what Observatory is asking you to do?",
        "Learn: can you tell the reasoning move from answer correctness?",
        "Model detail: does the first read stay readable before source-derived detail?",
        "Relation detail: does the plain-language story come before labels and confidence?",
        "Map: does navigation stay separate from graph-edge proof?",
        "Receipts: do custody and non-claims lead, with technical inspection optional?",
    ]:
        assert phrase in html

    assert html.index("Review prompts") < html.index("Focused hierarchy scorecard")
    assert html.index("Focused hierarchy scorecard") < html.index("What to record")


def test_blank_review_forms_carry_scorecard_without_positive_prefill() -> None:
    form_md = FORM_MD.read_text(encoding="utf-8")
    form_json = _load_json(FORM_JSON)
    manifest = _load_json(MANIFEST)

    assert "## Focused Hierarchy Scorecard" in form_md
    assert "### Model Detail Progressive Disclosure" in form_md
    assert "### Receipts Optional Inspection" in form_md
    assert "[x]" not in form_md.lower()

    assert list(form_json["focused_hierarchy_checks"].keys()) == list(
        FOCUSED_HIERARCHY_CHECKS
    )
    for review in form_json["focused_hierarchy_checks"].values():
        assert review["selected"] is None
        assert review["evidence"] == ""
    assert manifest["focused_hierarchy_checks"] == list(FOCUSED_HIERARCHY_CHECKS)
    assert (
        "docs/product/observatory-model-detail-overload-reduction-v0.md"
        in manifest["source_design_slices"]
    )
    assert (
        "docs/product/observatory-receipts-technical-inspection-disclosure-v0.md"
        in manifest["source_design_slices"]
    )


def test_intake_reports_focused_hierarchy_check_coverage() -> None:
    intake = validate_observatory_workspace_human_review_form(
        _completed_form(),
        source_ref="reviews/human/observatory-workspace/review.json",
        created_at="2026-07-07T00:00:00+00:00",
    )

    assert intake["intake_status"] == "accepted"
    assert intake["review_coverage"]["expected_focused_hierarchy_checks"] == list(
        FOCUSED_HIERARCHY_CHECKS
    )
    assert intake["review_coverage"]["reviewed_focused_hierarchy_checks"] == list(
        FOCUSED_HIERARCHY_CHECKS
    )
    assert intake["review_coverage"]["all_focused_hierarchy_checks_reviewed"] is True
    assert intake["downstream_allowed"]["can_plan_revision"] is True
    assert intake["downstream_allowed"]["can_expand_product"] is False


def test_scorecard_docs_review_and_boundaries_are_clean() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    assert "Observatory Workspace Human Hierarchy Scorecard" in readme
    assert "observatory-workspace-human-hierarchy-scorecard-v0.md" in readme
    assert review["decision_gate"] == (
        "ready_for_human_hierarchy_review_with_focused_scorecard"
    )
    assert review["focused_hierarchy_checks"] == list(FOCUSED_HIERARCHY_CHECKS)

    for phrase in [
        "first screen orientation",
        "Learn as a reasoning move, not answer correctness",
        "model detail progressive disclosure",
        "relation story before taxonomy",
        "Map as navigation, not proof",
        "Receipts as custody and optional inspection",
        "does not complete human review",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in doc

    assert review["implemented"]["review_guide_scorecard"] is True
    assert review["implemented"]["human_form_markdown_scorecard"] is True
    assert review["implemented"]["human_form_json_scorecard"] is True
    assert review["implemented"]["intake_focused_check_coverage"] is True
    assert review["implemented"]["human_form_prefilled"] is False
    assert review["implemented"]["human_review_completed"] is False
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["boundary"]["completes_human_review"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_scorecard_links_and_claims_are_clean() -> None:
    missing = []
    for path in [DOC, README, FORM_MD]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [DOC, FORM_MD, FORM_JSON, MANIFEST, REVIEW]
    )

    assert missing == []
    assert "/" + "Users/" not in text
    assert "Desktop/" + "Apps" not in text
    assert "product_proof\": true" not in text
    assert "human_validated\": true" not in text
    assert "answer_correctness\": true" not in text
    assert "advice_correctness\": true" not in text
    assert "runtime_integration_authorized\": true" not in text
    assert "action_authorized\": true" not in text
