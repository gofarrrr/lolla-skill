from __future__ import annotations

from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
RENDERED_EXAMPLES = {
    "ceo-remove-founding-cofounder": REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md",
    "launch-public-enterprise-beta": REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md",
    "deploy-assisted-intake-routing": REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md",
}
PATCH_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-plain-language-renderer-patch-v0.md"
)
RENDERER_DOC_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-renderer-v0.md"
)
REQUIRED_HEADINGS = (
    "## The decision",
    "## What changed",
    "## What this means for action",
    "## What still might be wrong",
    "## What this does not prove",
    "## Evidence and limits",
)
MAIN_BODY_FORBIDDEN_STRINGS = (
    "source_status:",
    "human_validated:",
    "product_proof:",
    "agent_action_authorized:",
    "schema_version",
    "artifact family",
    "custody machinery",
    "lane",
    "packet",
)
REQUIRED_NON_CLAIMS = (
    "not_correctness_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_human_validated_unless_marked",
    "clean_artifacts_do_not_imply_good_advice",
    "process_evidence_is_not_decision_certification",
    "llm_interpretation_is_provisional_unless_human_reviewed",
)
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _main_body(markdown: str) -> str:
    return markdown.split("## Evidence and limits", 1)[0]


def _evidence_and_limits(markdown: str) -> str:
    return markdown.split("## Evidence and limits", 1)[1]


def test_all_three_plain_language_rendered_examples_exist() -> None:
    for path in RENDERED_EXAMPLES.values():
        assert path.exists(), path
        assert _text(path).startswith("# Decision Work Brief\n\n")


def test_rendered_examples_use_plain_language_headings_in_order() -> None:
    for path in RENDERED_EXAMPLES.values():
        markdown = _text(path)
        positions = [markdown.index(heading) for heading in REQUIRED_HEADINGS]

        assert positions == sorted(positions)
        assert "## Starting Direction" not in markdown
        assert "## What Lolla Pressed On" not in markdown
        assert "## Evidence Receipt" not in markdown
        assert "## Custody And Limits" not in markdown


def test_main_body_does_not_foreground_internal_machinery_strings() -> None:
    for path in RENDERED_EXAMPLES.values():
        main_body = _main_body(_text(path)).lower()

        for forbidden in MAIN_BODY_FORBIDDEN_STRINGS:
            assert forbidden not in main_body


def test_rendered_examples_preserve_limits_in_evidence_section() -> None:
    for path in RENDERED_EXAMPLES.values():
        evidence = _evidence_and_limits(_text(path))

        assert "Human validation: no" in evidence
        assert "Product proof: no" in evidence
        assert "Answer-quality scoring: no" in evidence
        assert "Agent action authorization: no" in evidence
        assert "Runtime invoked: no" in evidence
        assert "Skill invoked: no" in evidence
        assert "Archive mutated: no" in evidence
        assert "Model calls: 0" in evidence
        assert "Source mode: checked-in-safe" in evidence
        assert "Private/raw content included: no" in evidence
        assert "Provider text included: no" in evidence
        assert "Section uncertainty" in evidence
        assert "Source references" in evidence


def test_rendered_examples_preserve_uncertainty_missingness_and_non_claims() -> None:
    for path in RENDERED_EXAMPLES.values():
        markdown = _text(path)

        assert "Uncertainty: " in markdown
        assert "Missing or uncertain:" in markdown
        assert "Not proven:" in markdown
        for non_claim in REQUIRED_NON_CLAIMS:
            assert non_claim in markdown


def test_rendered_examples_do_not_claim_validation_proof_or_agent_authorization() -> None:
    forbidden_claims = (
        "Human validation: yes",
        "Product proof: yes",
        "Agent action authorization: yes",
        "Lolla improved the decision",
        "proves Lolla improved",
        "proves product readiness",
        "clean artifacts prove good advice",
    )
    for path in RENDERED_EXAMPLES.values():
        markdown = _text(path)

        for claim in forbidden_claims:
            assert claim not in markdown


def test_rendered_examples_have_no_local_paths_or_private_markers() -> None:
    for path in RENDERED_EXAMPLES.values():
        markdown = _text(path)

        assert "/tmp/" not in markdown
        for marker in PRIVACY_MARKERS:
            assert marker not in markdown


def test_pr123_docs_and_rendered_examples_pass_product_delta_boundary_lint() -> None:
    paths = [PATCH_DOC_PATH, RENDERER_DOC_PATH, *RENDERED_EXAMPLES.values()]

    report = lint_product_delta_paths(paths)

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
