from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/evals/capture_observatory_workspace_human_review.py"
FORM_JSON = (
    REPO_ROOT
    / "docs/product/observatory-workspace-user-review-packet-v0/human-review-form.json"
)
DOC = REPO_ROOT / "docs/product/observatory-workspace-human-review-capture-path-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-workspace-human-review-capture-path-v0/review.json"
)
SURFACES = ["Outcome", "Learn", "Models", "Relations", "Map", "Receipts"]
FOCUSED_CHECKS = [
    "first_screen_orientation",
    "learn_reasoning_move_not_answer_correctness",
    "model_detail_progressive_disclosure",
    "relation_story_before_taxonomy",
    "map_navigation_not_proof",
    "receipts_optional_inspection",
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _completed_form() -> dict:
    form = copy.deepcopy(_load_json(FORM_JSON))
    form["status"] = "completed_human_review"
    form["human_review_completed"] = True
    form["workspace_reviewed"] = {
        "case_id": "launch-public-enterprise-beta",
        "run_id": "20260627T104146Z_7bfe79",
        "review_date": "2026-07-07",
        "reviewer": "human-reviewer",
    }
    form["overall_decision"]["selected"] = "ready_to_continue_with_caveats"
    form["overall_decision"]["notes"] = "Usable with hierarchy caveats."
    form["first_impression"] = {
        "page_purpose_in_first_ten_seconds": "A run learning workspace.",
        "wanted_next_click": "Outcome.",
        "one_product_or_artifact_pile": "Mostly one product surface.",
    }
    form["progression_review"]["selected"] = "adequate"
    form["progression_review"]["evidence"] = (
        "Outcome to Learn to supporting surfaces is understandable."
    )
    for surface in SURFACES:
        form["surface_reviews"][surface]["selected"] = "adequate"
        form["surface_reviews"][surface]["what_worked"] = (
            f"{surface} has a recognizable job."
        )
        form["surface_reviews"][surface]["what_should_change"] = ""
    for check in FOCUSED_CHECKS:
        form["focused_hierarchy_checks"][check]["selected"] = "adequate"
        form["focused_hierarchy_checks"][check]["evidence"] = (
            f"{check} keeps the first read ahead of details."
        )
    form["information_hierarchy"]["selected"] = "adequate"
    form["information_hierarchy"]["evidence"] = (
        "The hierarchy is visible after one pass."
    )
    form["non_claims_review"]["selected"] = "yes"
    form["non_claims_review"]["evidence"] = (
        "The workspace avoids proof, correctness, and action claims."
    )
    return form


def _run_capture(review_path: Path, out_path: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--review",
            str(review_path),
            "--out",
            str(out_path),
            *extra,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_capture_cli_writes_accepted_sanitized_intake(tmp_path: Path) -> None:
    review_path = _write_json(tmp_path / "review.json", _completed_form())
    out_path = tmp_path / "intake.json"

    result = _run_capture(
        review_path,
        out_path,
        "--source-ref",
        "reviews/human/observatory-workspace/review.json",
        "--created-at",
        "2026-07-07T00:00:00+00:00",
    )

    assert result.returncode == 0, result.stderr
    payload = _load_json(out_path)
    assert payload["schema_version"] == "lolla.observatory_workspace_human_review_intake.v0"
    assert payload["intake_status"] == "accepted"
    assert payload["accepted_for_downstream"] is True
    assert payload["next_gate"] == "ready_to_plan_next_observatory_slice_with_human_caveats"
    assert payload["intake_metadata"]["source_ref"] == (
        "reviews/human/observatory-workspace/review.json"
    )
    assert payload["intake_metadata"]["created_at"] == "2026-07-07T00:00:00+00:00"
    assert payload["review_coverage"]["all_surfaces_reviewed"] is True
    assert payload["review_coverage"]["all_focused_hierarchy_checks_reviewed"] is True
    assert payload["downstream_allowed"]["can_plan_revision"] is True
    assert payload["downstream_allowed"]["can_expand_product"] is False
    assert payload["downstream_allowed"]["can_claim_human_validation"] is False
    assert payload["downstream_allowed"]["can_wire_runtime"] is False
    assert payload["downstream_allowed"]["can_authorize_action"] is False
    assert payload["boundary"]["runs_lolla"] is False
    assert payload["boundary"]["calls_provider_or_model"] is False


def test_capture_cli_keeps_blank_review_blocked(tmp_path: Path) -> None:
    review_path = _write_json(tmp_path / "blank-review.json", _load_json(FORM_JSON))
    out_path = tmp_path / "blank-intake.json"

    result = _run_capture(
        review_path,
        out_path,
        "--created-at",
        "2026-07-07T00:00:00+00:00",
    )

    assert result.returncode == 0, result.stderr
    payload = _load_json(out_path)
    assert payload["intake_status"] == "blocked_pending_human_review"
    assert payload["accepted_for_downstream"] is False
    assert payload["repair_required"] is True
    assert payload["blocker_reasons"] == ["human_review_not_completed"]
    assert payload["next_gate"] == "needs_human_review_before_observatory_expansion"
    assert payload["intake_metadata"]["source_ref"] == "blank-review.json"
    assert payload["downstream_allowed"]["can_plan_revision"] is False
    assert payload["downstream_allowed"]["can_expand_product"] is False


def test_capture_cli_blocks_privacy_risk_without_leaking_source_or_review_text(
    tmp_path: Path,
) -> None:
    form = _completed_form()
    form["overall_decision"]["notes"] = "private " + "api" + "_key marker"
    review_path = _write_json(tmp_path / "private-review.json", form)
    out_path = tmp_path / "private-intake.json"

    result = _run_capture(
        review_path,
        out_path,
        "--source-ref",
        "/" + "Users/example/private-review.json",
        "--created-at",
        "2026-07-07T00:00:00+00:00",
    )

    assert result.returncode == 0, result.stderr
    rendered = out_path.read_text(encoding="utf-8")
    payload = json.loads(rendered)
    assert payload["intake_status"] == "blocked_privacy_risk"
    assert payload["accepted_for_downstream"] is False
    assert "privacy_marker_detected" in payload["blocker_reasons"]
    assert payload["intake_metadata"]["source_ref"] == "redacted_unsafe_source_ref"
    assert "/" + "Users/" not in rendered
    assert "api" + "_key" not in rendered
    assert "private-review" not in rendered


def test_capture_cli_reports_read_errors_without_writing_output(tmp_path: Path) -> None:
    review_path = tmp_path / "not-json.json"
    review_path.write_text("{not json", encoding="utf-8")
    out_path = tmp_path / "intake.json"

    result = _run_capture(review_path, out_path)

    assert result.returncode == 2
    assert "error: review form is not valid JSON" in result.stderr
    assert not out_path.exists()


def test_capture_path_docs_review_and_readme_capture_boundaries() -> None:
    doc = DOC.read_text(encoding="utf-8")
    normalized_doc = " ".join(doc.split())
    readme = README.read_text(encoding="utf-8")
    review = _load_json(REVIEW)

    assert "Observatory Workspace Human Review Capture Path" in readme
    assert "observatory-workspace-human-review-capture-path-v0.md" in readme
    assert review["decision_gate"] == (
        "ready_to_capture_completed_human_hierarchy_review_intake"
    )

    for phrase in [
        "operator-safe way to turn a filled JSON review form into a deterministic intake artifact",
        "capture_observatory_workspace_human_review.py",
        "records only the review filename, not the local filesystem path",
        "blocks blank, incomplete, unsafe, or boundary-violating forms",
        "redacts unsafe source refs",
        "does not complete human review",
        "does not run Lolla",
        "does not invoke the Lolla skill",
        "does not call providers or model APIs",
        "does not wire skill runtime behavior",
        "does not edit `observatory/build`",
        "does not claim product proof",
        "does not claim human validation",
    ]:
        assert phrase in normalized_doc

    assert review["implemented"]["offline_operator_capture_cli"] is True
    assert review["implemented"]["reads_completed_human_review_json"] is True
    assert review["implemented"]["writes_sanitized_intake_json"] is True
    assert review["implemented"]["blocks_blank_forms"] is True
    assert review["implemented"]["blocks_privacy_risk_forms"] is True
    assert review["implemented"]["redacts_unsafe_source_refs"] is True
    assert review["implemented"]["runtime_behavior_changed"] is False
    assert review["boundary"]["completes_human_review"] is False
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


def test_capture_path_links_and_claims_are_clean() -> None:
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
        path.read_text(encoding="utf-8")
        for path in [DOC, REVIEW, SCRIPT]
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
