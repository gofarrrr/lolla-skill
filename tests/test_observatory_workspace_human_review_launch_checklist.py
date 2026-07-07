from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = (
    REPO_ROOT
    / "docs/product/observatory-workspace-human-review-launch-checklist-v0.md"
)
MANIFEST = (
    REPO_ROOT
    / "docs/product/observatory-workspace-human-review-launch-checklist-v0.json"
)
README = REPO_ROOT / "docs/product/README.md"
HUMAN_README = REPO_ROOT / "reviews/human/observatory-workspace/README.md"
CODEX_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "observatory-workspace-human-review-launch-checklist-v0/review.json"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_launch_checklist_is_indexed_and_states_review_only_scope() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    human_readme = HUMAN_README.read_text(encoding="utf-8")
    manifest = _load_json(MANIFEST)
    review = _load_json(CODEX_REVIEW)

    assert "Observatory Workspace Human Review Launch Checklist" in doc
    assert "Observatory Workspace Human Review Launch Checklist" in readme
    assert "observatory-workspace-human-review-launch-checklist-v0.md" in readme
    assert "observatory-workspace-human-review-launch-checklist-v0.json" in readme
    assert "Launch checklist" in human_readme
    assert "observatory-workspace-human-review-launch-checklist-v0.md" in human_readme
    assert manifest["decision_gate"] == "ready_to_launch_real_human_hierarchy_review"
    assert review["decision_gate"] == "ready_to_launch_real_human_hierarchy_review"
    assert manifest["next_gate"] == "awaiting_real_human_hierarchy_review_response"
    assert review["next_gate"] == "awaiting_real_human_hierarchy_review_response"
    assert "review launch checklist only; no completed human review" in doc
    assert "This checklist is review enablement only." in doc


def test_launch_checklist_names_exact_server_command_routes_and_click_order() -> None:
    doc = DOC.read_text(encoding="utf-8")
    normalized = " ".join(doc.split())
    manifest = _load_json(MANIFEST)
    review = _load_json(CODEX_REVIEW)

    for phrase in [
        "python3 observatory/serve_result.py",
        "--result \"$LOLLA_OBSERVATORY_REVIEW_RESULT\"",
        "--port 8080",
        "http://localhost:8080/review/observatory-workspace?case_id=<case-id>",
        "launch-public-enterprise-beta",
        "Review Guide -> Outcome -> Learn -> Models -> model detail -> Relations -> relation detail -> Map -> Receipts",
        "Outcome -> Learn -> Models -> Relations -> Map -> Receipts",
        "Extraction audit -> Usage -> Advanced audit",
    ]:
        assert phrase in normalized

    assert manifest["launch_command"] == [
        "python3",
        "observatory/serve_result.py",
        "--result",
        "$LOLLA_OBSERVATORY_REVIEW_RESULT",
        "--port",
        "8080",
    ]
    assert manifest["start_route_template"] == (
        "http://localhost:8080/review/observatory-workspace?case_id=<case-id>"
    )
    assert manifest["pilot_case_id_example"] == "launch-public-enterprise-beta"
    assert manifest["normal_product_journey"] == [
        "Outcome",
        "Learn",
        "Models",
        "Relations",
        "Map",
        "Receipts",
    ]
    assert manifest["review_clickthrough_order"] == [
        "Review Guide",
        "Outcome",
        "Learn",
        "Models",
        "model detail",
        "Relations",
        "relation detail",
        "Map",
        "Receipts",
    ]
    assert review["launch_path"]["server"] == "observatory/serve_result.py"
    assert review["launch_path"]["requires_existing_result_json"] is True


def test_launch_checklist_records_form_capture_paths_without_fake_review() -> None:
    doc = DOC.read_text(encoding="utf-8")
    normalized = " ".join(doc.split())
    manifest = _load_json(MANIFEST)
    review = _load_json(CODEX_REVIEW)

    for phrase in [
        "docs/product/observatory-workspace-user-review-packet-v0/human-review-form.json",
        "reviews/human/observatory-workspace/review.json",
        "reviews/human/observatory-workspace/intake.json",
        "capture_observatory_workspace_human_review.py",
        "Negative, partial, and `cannot_judge` answers are useful.",
        "Do not pre-fill a positive result.",
    ]:
        assert phrase in normalized

    assert manifest["review_output"]["blank_form"] == (
        "docs/product/observatory-workspace-user-review-packet-v0/human-review-form.json"
    )
    assert manifest["review_output"]["completed_review"] == (
        "reviews/human/observatory-workspace/review.json"
    )
    assert manifest["review_output"]["captured_intake"] == (
        "reviews/human/observatory-workspace/intake.json"
    )
    assert manifest["implemented"]["completed_review_added"] is False
    assert manifest["implemented"]["captured_intake_added"] is False
    assert review["implemented"]["completed_review_present_in_this_slice"] is False
    assert review["implemented"]["intake_present_in_this_slice"] is False


def test_launch_checklist_boundaries_and_non_claims_are_preserved() -> None:
    doc = DOC.read_text(encoding="utf-8")
    normalized = " ".join(doc.split())
    manifest = _load_json(MANIFEST)
    review = _load_json(CODEX_REVIEW)

    for phrase in [
        "does not add a completed review or intake artifact",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not create a new run",
        "does not generate or attach sidecars",
        "does not wire skill runtime behavior",
        "does not mutate archives",
        "does not edit `observatory/build`",
        "does not touch `SKILL.md`",
        "does not touch `scripts/skill/*`",
        "does not touch `scripts/archive_run.py`",
        "does not claim product proof",
        "does not claim human validation",
        "does not claim answer correctness",
        "does not claim advice correctness",
        "does not authorize automatic action",
    ]:
        assert phrase in normalized

    for payload in [manifest, review]:
        assert payload["boundary"]["adds_completed_review_or_intake"] is False
        assert payload["boundary"]["runs_lolla"] is False
        assert payload["boundary"]["invokes_lolla_skill"] is False
        assert payload["boundary"]["calls_provider_or_model"] is False
        assert payload["boundary"]["creates_new_run"] is False
        assert payload["boundary"]["generates_sidecars"] is False
        assert payload["boundary"]["wires_skill_runtime_behavior"] is False
        assert payload["boundary"]["mutates_archives"] is False
        assert payload["boundary"]["compiled_spa_bundle_changed"] is False
        assert payload["boundary"]["touches_skill_md"] is False
        assert payload["boundary"]["touches_scripts_skill"] is False
        assert payload["boundary"]["touches_archive_run"] is False
        assert payload["non_claims"]["product_proof"] is False
        assert payload["non_claims"]["human_validated"] is False
        assert payload["non_claims"]["answer_correctness"] is False
        assert payload["non_claims"]["advice_correctness"] is False
        assert payload["non_claims"]["runtime_integration_authorized"] is False
        assert payload["non_claims"]["action_authorized"] is False


def test_launch_checklist_links_json_and_private_markers_are_clean() -> None:
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
        for path in [DOC, MANIFEST, CODEX_REVIEW, HUMAN_README]
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
