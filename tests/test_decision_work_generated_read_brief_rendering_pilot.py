from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-brief-rendering-pilot-v0.md"
)
RENDERED_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-brief-rendering-pilot-v0/review.json"
)
PR186_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-brief-supply-adapter-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
FORBIDDEN_STRINGS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _review() -> dict:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def test_review_json_records_pr187_schema_and_gate() -> None:
    review = _review()

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_brief_rendering_pilot.v0"
    )
    assert review["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert review["rendering_status"] == "rendered_from_generated_read_supply"
    assert review["rendered_brief_ref"] == (
        "docs/conversation-understanding/"
        "decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md"
    )
    assert review["uncertainty_preserved"] is True
    assert review["privacy_limits_preserved"] is True
    assert review["source_refs_preserved"] is True
    assert review["non_claims_preserved"] is True
    assert review["decision_gate"] == (
        "proceed_to_generated_read_brief_vs_existing_brief_review"
    )
    assert (
        review["recommended_next_pr"]
        == "PR188 Decision Work Generated Read Brief vs Existing Brief Review v0"
    )


def test_review_json_preserves_conservative_boundaries() -> None:
    review = _review()
    custody = review["custody_flags"]
    downstream = review["downstream_boundary"]

    assert custody["model_calls"] == 0
    assert custody["runtime_invoked"] is False
    assert custody["skill_invoked"] is False
    assert custody["archive_mutated"] is False
    assert custody["brief_enriched"] is False
    assert custody["triage_generated"] is False
    assert custody["resolver_refs_marked_usable"] is False
    assert custody["runtime_sidecar_updated"] is False
    assert custody["product_proof"] is False
    assert custody["human_validated"] is False
    assert custody["answer_quality_scored"] is False
    assert custody["agent_action_authorized"] is False
    assert custody["automatic_action_authorized"] is False
    assert downstream["can_enrich_brief"] is False
    assert downstream["can_generate_triage"] is False
    assert downstream["can_mark_resolver_refs_usable"] is False
    assert downstream["can_update_runtime_sidecar"] is False
    assert downstream["can_call_models"] is False
    assert downstream["can_authorize_agent_action"] is False


def test_rendered_brief_has_required_sections_and_boundaries() -> None:
    markdown = RENDERED_PATH.read_text(encoding="utf-8")

    for heading in (
        "# Decision Work Generated Read Brief",
        "## The decision",
        "## What the generated interpretation adds",
        "## What changed for action",
        "## What still might be wrong",
        "## What this does not prove",
        "## Evidence and limits",
    ):
        assert heading in markdown
    assert "launch-public-enterprise-beta" in markdown
    assert "Source references" in markdown
    assert "Uncertainty: medium." in markdown
    assert "Privacy limit:" in markdown
    assert "Product proof: no" in markdown
    assert "Human validation: no" in markdown
    assert "Answer-quality scoring: no" in markdown
    assert "Agent action authorization: no" in markdown
    assert "Runtime sidecar update allowed: no" in markdown
    assert "proof that the interpretation is true" in markdown


def test_rendered_brief_excludes_unsafe_markers_and_runtime_authority() -> None:
    markdown = RENDERED_PATH.read_text(encoding="utf-8")

    for marker in FORBIDDEN_STRINGS:
        assert marker not in markdown
    assert "runtime sidecar update" in markdown.lower()
    assert "Agent action authorization: no" in markdown
    assert "approval" not in markdown.lower()
    assert "certification" not in markdown.lower()


def test_discoverability_docs_reference_pr187() -> None:
    expected = "Decision Work Generated Read Brief Rendering Pilot"
    for path in (
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
        PRD_PATH,
        PR186_DOC,
        DOC_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr187_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            RENDERED_PATH,
            REVIEW_PATH,
            PR186_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr187_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        RENDERED_PATH,
        REVIEW_PATH,
        REPO_ROOT / "engine/system_b/decision_work_generated_read_brief_renderer.py",
        REPO_ROOT / "scripts/evals/render_decision_work_generated_read_brief.py",
        REPO_ROOT / "tests/test_decision_work_generated_read_brief_renderer.py",
        PR186_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
