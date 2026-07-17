from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-brief-vs-existing-brief-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-brief-vs-existing-brief-review-v0/review.json"
)
GENERATED_BRIEF = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md"
)
EXISTING_BRIEF = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
)
ENRICHED_BRIEF = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md"
)
PR187_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-brief-rendering-pilot-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-prd-v0.md"
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


def test_review_json_schema_gate_and_refs() -> None:
    review = _review()

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_brief_vs_existing_brief_review.v0"
    )
    assert review["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert review["generated_read_brief_ref"] == (
        "docs/conversation-understanding/"
        "decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md"
    )
    assert review["existing_rendered_brief_ref"] == (
        "docs/conversation-understanding/"
        "decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
    )
    assert review["existing_enriched_brief_ref"] == (
        "docs/conversation-understanding/"
        "decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md"
    )
    assert review["comparison_status"] == "coherent_for_second_case_pilot"
    assert review["decision_gate"] == (
        "proceed_to_second_generated_read_brief_rendering_pilot"
    )
    assert (
        review["recommended_next_pr"]
        == "PR189 Second Generated Read Brief Rendering Pilot v0"
    )


def test_review_records_preservation_and_caveats() -> None:
    review = _review()

    assert review["preserved_decision_question"]["status"] == "preserved"
    assert review["preserved_action_consequence"]["status"] == "preserved"
    assert review["preserved_uncertainty"] is True
    assert review["preserved_privacy_limits"] is True
    assert review["preserved_non_claims"] is True
    assert review["caveats_lost_or_weakened"]
    assert review["useful_additions"]
    assert "readable enough to feel authoritative" in review["overclaim_or_overtrust_risk"]
    assert "checked-in-safe generated-read supply" in review["source_depth_risk"]


def test_review_preserves_conservative_boundary_flags() -> None:
    review = _review()
    custody = review["custody_flags"]
    downstream = review["downstream_boundary"]

    assert custody["model_calls"] == 0
    assert custody["runtime_invoked"] is False
    assert custody["skill_invoked"] is False
    assert custody["archive_mutated"] is False
    assert custody["generated_read_created"] is False
    assert custody["second_case_rendered"] is False
    assert custody["brief_enriched"] is False
    assert custody["triage_generated"] is False
    assert custody["resolver_refs_marked_usable"] is False
    assert custody["runtime_sidecar_updated"] is False
    assert custody["product_proof"] is False
    assert custody["human_validated"] is False
    assert custody["answer_quality_scored"] is False
    assert custody["agent_action_authorized"] is False
    assert custody["automatic_action_authorized"] is False
    assert downstream["can_run_second_case_rendering_pilot"] is True
    assert downstream["can_enrich_brief"] is False
    assert downstream["can_generate_triage"] is False
    assert downstream["can_mark_resolver_refs_usable"] is False
    assert downstream["can_update_runtime_sidecar"] is False
    assert downstream["can_call_models"] is False
    assert downstream["can_authorize_agent_action"] is False


def test_compared_briefs_preserve_core_decision_and_action_language() -> None:
    generated = GENERATED_BRIEF.read_text(encoding="utf-8")
    existing = EXISTING_BRIEF.read_text(encoding="utf-8")
    enriched = ENRICHED_BRIEF.read_text(encoding="utf-8")

    for text in (generated, existing, enriched):
        assert "public enterprise beta" in text
        assert "private" in text
        assert "proof" in text
        assert "Uncertainty:" in text
    assert "proof-producing buyer behavior" in generated
    assert "proof-producing buyer behavior" in enriched
    assert "public launch" in existing
    assert "What this does not prove" in generated


def test_review_doc_records_the_comparison_and_gate() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Generated Read Brief vs Existing Brief Review v0" in text
    assert "Generated-read rendered launch-beta brief" in text
    assert "Existing launch-beta rendered brief" in text
    assert "Existing launch-beta enriched brief" in text
    assert "proceed_to_second_generated_read_brief_rendering_pilot" in text
    assert "PR189 Second Generated Read Brief Rendering Pilot v0" in text
    assert "does not modify the rendered brief" in text
    assert "does not" in text
    assert "claim semantic correctness" in text


def test_discoverability_docs_reference_pr188() -> None:
    expected = "Decision Work Generated Read Brief vs Existing Brief Review"
    for path in (
        PROGRESS_PATH,
        BOARD_README_PATH,
        PRD_PATH,
        PR187_DOC,
        DOC_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr188_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            GENERATED_BRIEF,
            EXISTING_BRIEF,
            ENRICHED_BRIEF,
            PR187_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr188_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        GENERATED_BRIEF,
        PR187_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
