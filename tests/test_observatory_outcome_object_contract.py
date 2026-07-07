from __future__ import annotations

import json
import re
from pathlib import Path

from observatory.product_view_adapters import build_observatory_product_view_response
from observatory.product_views import (
    OUTCOME_VALUE_SCHEMA_VERSION,
    validate_outcome_value,
    validate_workspace,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/observatory-outcome-object-contract-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-outcome-object-contract-v0/review.json"
)


def _launch_result() -> dict:
    return {
        "usage_summary": {"run_id": "20260627T104146Z_7bfe79"},
        "extraction": {
            "decision_situation": "A public enterprise beta launch is being reviewed."
        },
        "run_health": {"overall": "healthy", "issues": []},
        "revised_answer": (
            "Launch in stages after the support risk is made explicit. "
            "Keep the first cohort narrow and treat the beta as a learning gate. "
            "Do not treat enterprise interest as proof of readiness."
        ),
        "memo_what_changed": (
            "The answer changed because authority and enterprise posture were "
            "separated from evidence."
        ),
        "delta_card": {
            "top_findings": [
                {
                    "description": (
                        "Authority pressure was doing too much work in the launch plan."
                    )
                }
            ]
        },
    }


def _workspace() -> dict:
    response = build_observatory_product_view_response(
        selected_case_id="archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        result=_launch_result(),
    )
    return validate_workspace(response["workspace"])


def test_adapter_builds_full_outcome_value_without_clipping() -> None:
    outcome = validate_outcome_value(_workspace()["outcome_value"])

    assert outcome["schema_version"] == OUTCOME_VALUE_SCHEMA_VERSION
    assert outcome["outcome_headline"] == (
        "Launch in stages after the support risk is made explicit."
    )
    assert outcome["plain_language_answer"] == _launch_result()["revised_answer"]
    assert "..." not in outcome["outcome_headline"]
    assert "..." not in outcome["plain_language_answer"]
    assert outcome["what_changed"] == [
        "The answer changed because authority and enterprise posture were separated from evidence."
    ]
    assert outcome["primary_reasons"] == [
        "Keep the first cohort narrow and treat the beta as a learning gate.",
        "Do not treat enterprise interest as proof of readiness.",
    ]
    assert outcome["confidence_boundary"][:2] == [
        "Launch in stages after the support risk is made explicit.",
        "Keep the first cohort narrow and treat the beta as a learning gate.",
    ]
    assert [move["label"] for move in outcome["recommended_next_moves"]] == [
        "Practice the reasoning move",
        "Inspect receipts",
        "Download MD",
    ]


def test_outcome_value_preserves_missingness_without_faking_copy() -> None:
    result = _launch_result()
    result.pop("revised_answer")
    result.pop("memo_what_changed")

    response = build_observatory_product_view_response(
        selected_case_id="archive:launch-public-enterprise-beta:20260627T104146Z_7bfe79",
        result=result,
    )
    outcome = validate_outcome_value(response["workspace"]["outcome_value"])

    assert outcome["stance"] == "missing_revised_answer"
    assert outcome["plain_language_answer"] == (
        "No revised answer artifact is available for this selected run."
    )
    assert "revised_answer" in outcome["missingness"]["missing_fields"]
    assert "memo_what_changed" in outcome["missingness"]["missing_fields"]
    assert outcome["primary_reasons"] == [
        "Authority pressure was doing too much work in the launch plan."
    ]
    assert outcome["what_changed"] == [
        "The run made this pressure explicit: Authority pressure was doing too much work in the launch plan."
    ]


def test_doc_readme_and_review_capture_outcome_stop_line() -> None:
    doc = DOC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))

    assert "Observatory Outcome Object Contract" in readme
    assert "observatory-outcome-object-contract-v0.md" in readme
    assert review["decision_gate"] == "proceed_to_outcome_first_viewport_redesign"
    assert review["implemented"]["outcome_value_validator"] is True
    assert review["implemented"]["renderer_changed"] is False
    assert review["product_intent"]["outcome_owns_actual_run_answer"] is True

    for phrase in [
        "outcome_value",
        "Outcome should answer:",
        "plain_language_answer",
        "confidence_boundary",
        "recommended_next_moves",
        "The current reading-path panels",
        "This PR stops before:",
        "Outcome page rendering",
        "does not claim answer correctness",
    ]:
        assert phrase in doc

    assert review["boundary"]["runs_lolla"] is False
    assert review["boundary"]["invokes_lolla_skill"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["renders_html"] is False
    assert review["boundary"]["touches_skill_md"] is False
    assert review["boundary"]["touches_scripts_skill"] is False
    assert review["boundary"]["touches_archive_run"] is False
    assert review["boundary"]["touches_compiled_spa_bundle"] is False


def test_outcome_object_doc_links_are_local() -> None:
    missing = []
    for path in [DOC, README]:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith("#") or re.match(r"^[a-z]+:", target):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).exists():
                missing.append((path.name, clean))
    assert missing == []
