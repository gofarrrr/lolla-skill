from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-workspace-human-review-instructions-v0.md"
README = REPO_ROOT / "docs/product/README.md"
HUMAN_README = REPO_ROOT / "reviews/human/observatory-workspace/README.md"
REVIEW_JSON = REPO_ROOT / "reviews/human/observatory-workspace/review.json"
INTAKE_JSON = REPO_ROOT / "reviews/human/observatory-workspace/intake.json"
CODEX_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-human-review-instructions-v0/review.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_human_review_instruction_paths_are_documented_without_fake_outputs() -> None:
    doc = DOC.read_text(encoding="utf-8")
    human = HUMAN_README.read_text(encoding="utf-8")
    review = _load_json(CODEX_REVIEW)

    for text in [doc, human]:
        assert "reviews/human/observatory-workspace/review.json" in text
        assert "reviews/human/observatory-workspace/intake.json" in text
        assert (
            "docs/product/observatory-workspace-user-review-packet-v0/"
            "human-review-form.json"
        ) in text
        assert "capture_observatory_workspace_human_review.py" in text
        assert "Outcome -> Learn -> Models -> Relations -> Map -> Receipts" in text

    assert not REVIEW_JSON.exists()
    assert not INTAKE_JSON.exists()
    assert review["implemented"]["review_json_created"] is False
    assert review["implemented"]["intake_json_created"] is False
    assert review["expected_future_files"] == [
        "reviews/human/observatory-workspace/review.json",
        "reviews/human/observatory-workspace/intake.json",
    ]


def test_human_review_instructions_explain_review_and_capture_sequence() -> None:
    human = HUMAN_README.read_text(encoding="utf-8")
    normalized_human = " ".join(human.split())

    for phrase in [
        "Status: instructions only; no completed human review is included here.",
        "Use this folder only when a real human reviewer has completed",
        "Do not pre-fill a positive result.",
        "Do not create `review.json` or `intake.json` until a real completed review exists.",
        "python3 scripts/evals/capture_observatory_workspace_human_review.py",
        "--review reviews/human/observatory-workspace/review.json",
        "--out reviews/human/observatory-workspace/intake.json",
        "--source-ref reviews/human/observatory-workspace/review.json",
    ]:
        assert phrase in normalized_human

    for status in [
        "`accepted`",
        "`blocked_pending_human_review`",
        "`blocked_privacy_risk`",
        "`rejected_invalid_review_form`",
        "`rejected_boundary_claim`",
    ]:
        assert status in human


def test_product_doc_and_review_json_capture_gate_and_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    normalized_doc = " ".join(doc.split())
    readme = README.read_text(encoding="utf-8")
    review = _load_json(CODEX_REVIEW)

    assert "Observatory Workspace Human Review Instructions" in readme
    assert "observatory-workspace-human-review-instructions-v0.md" in readme
    assert review["decision_gate"] == "ready_for_real_human_hierarchy_review_response"
    assert review["implemented"]["human_review_folder_readme"] is True
    assert review["implemented"]["reviewer_workflow_documented"] is True
    assert review["implemented"]["completed_review_path_documented"] is True
    assert review["implemented"]["intake_capture_command_documented"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False

    for phrase in [
        "The missing piece was a concrete handoff location and operator instruction set.",
        "Those files are not created in this slice.",
        "accepted intake can plan the next product revision gate",
        "does not complete human review",
        "does not add `reviews/human/observatory-workspace/review.json`",
        "does not add `reviews/human/observatory-workspace/intake.json`",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in normalized_doc

    assert review["boundary"]["completes_human_review"] is False
    assert review["boundary"]["adds_completed_review_json"] is False
    assert review["boundary"]["adds_intake_json"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["wires_skill_runtime_behavior"] is False
    assert review["boundary"]["touches_scripts_skill"] is False
    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["action_authorized"] is False


def test_instruction_links_and_claims_are_clean() -> None:
    missing = []
    for path in [DOC, README, HUMAN_README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [DOC, HUMAN_README, CODEX_REVIEW]
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
