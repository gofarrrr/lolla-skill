from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = (
    REPO_ROOT
    / "docs/product/observatory-workspace-human-review-awaiting-response-gate-v0.md"
)
README = REPO_ROOT / "docs/product/README.md"
CODEX_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "observatory-workspace-human-review-awaiting-response-gate-v0/review.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_awaiting_response_gate_is_indexed_and_names_the_pause_state() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = _load_json(CODEX_REVIEW)

    assert "Observatory Workspace Human Review Awaiting Response Gate" in doc
    assert "Observatory Workspace Human Review Awaiting Response Gate" in readme
    assert "observatory-workspace-human-review-awaiting-response-gate-v0.md" in readme
    assert (
        review["decision_gate"]
        == "awaiting_real_human_hierarchy_review_response"
    )
    assert (
        "The review scaffold is ready, but the real human response is still absent."
        in doc
    )
    assert "This slice does not add a completed review or intake artifact." in doc


def test_gate_documents_review_inputs_and_allowed_next_work() -> None:
    doc = DOC.read_text(encoding="utf-8")
    normalized = " ".join(doc.split())
    review = _load_json(CODEX_REVIEW)

    for phrase in [
        "reviews/human/observatory-workspace/review.json",
        "reviews/human/observatory-workspace/intake.json",
        "capture_observatory_workspace_human_review.py",
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "Do not add another UX expansion PR before the review response",
        "fixes a blocker found while attempting the review",
    ]:
        assert phrase in normalized

    assert review["implemented"]["review_scaffold_ready"] is True
    assert review["implemented"]["awaiting_response_gate_documented"] is True
    assert review["implemented"]["completed_review_present_in_this_slice"] is False
    assert review["implemented"]["intake_present_in_this_slice"] is False
    assert review["blocked_until"] == [
        "reviews/human/observatory-workspace/review.json",
        "reviews/human/observatory-workspace/intake.json",
    ]
    assert review["allowed_next_work"] == [
        "collect_real_human_review_response",
        "capture_human_review_intake",
        "fix_blocker_found_during_review_attempt",
    ]
    assert "additional_observatory_ux_expansion" in review[
        "disallowed_next_work_without_review"
    ]
    assert "runtime_integration" in review["disallowed_next_work_without_review"]


def test_gate_preserves_runtime_and_product_claim_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    normalized = " ".join(doc.split())
    review = _load_json(CODEX_REVIEW)

    for phrase in [
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not touch `SKILL.md`",
        "does not touch `scripts/skill/*`",
        "does not touch `scripts/archive_run.py`",
        "does not claim product proof",
        "does not claim human validation",
        "does not claim answer correctness",
        "does not claim advice correctness",
        "does not authorize automatic action",
        "This gate is not evidence of",
    ]:
        assert phrase in normalized

    assert review["boundary"]["adds_completed_review_or_intake"] is False
    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["wires_skill_runtime_behavior"] is False
    assert review["boundary"]["compiled_spa_bundle_changed"] is False
    assert review["boundary"]["touches_skill_md"] is False
    assert review["boundary"]["touches_scripts_skill"] is False
    assert review["boundary"]["touches_archive_run"] is False

    assert review["non_claims"]["product_proof"] is False
    assert review["non_claims"]["human_validated"] is False
    assert review["non_claims"]["answer_correctness"] is False
    assert review["non_claims"]["advice_correctness"] is False
    assert review["non_claims"]["runtime_integration_authorized"] is False
    assert review["non_claims"]["action_authorized"] is False
    assert review["non_claims"]["graph_edges_are_proof"] is False
    assert review["non_claims"]["relation_confidence_is_certification"] is False


def test_gate_links_and_private_markers_are_clean() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                missing.append(f"{path}: {target}")

    text = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC, CODEX_REVIEW]
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
