from __future__ import annotations

import re
from pathlib import Path

from engine.system_b.decision_work_brief_enrichment import (
    enrich_decision_work_brief_markdown,
    load_json_object,
    load_markdown,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json"
)
LAUNCH_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
)
DEPLOY_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md"
)
LAUNCH_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json"
)
DEPLOY_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json"
)
GENERATED_LAUNCH_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md"
)
GENERATED_DEPLOY_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md"
)
PATCH_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-builder-rule-patch-v0.md"
)
BUILDER_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-offline-enriched-builder-v0.md"
)
PR141_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enriched-builder-output-review-v0.md"
)
PR141_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-enriched-builder-output-review-v0/review.json"
)
EVIDENCE_ONLY_FIELD_NAMES = (
    "live_options",
    "abandoned_or_rejected_options",
    "noisy_friction",
    "lost_value",
)
FORBIDDEN_MAIN_BODY_STRINGS = (
    "The interpretation read frames",
    "Visible decision thresholds include",
    "Visible evidence gates include",
    "quality score",
    "source_status:",
    "field_group",
    "approval",
    "certification",
    "agent action authorization",
    "product proof",
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


def _main_enrichment_section(markdown: str) -> str:
    start = markdown.index("## What the interpretation adds")
    end = markdown.index("## What still might be wrong")
    return markdown[start:end]


def _sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if sentence.strip()
    ]


def test_patched_builder_keeps_one_enrichment_section_and_preserves_limits() -> None:
    original = load_markdown(LAUNCH_BRIEF_PATH)
    enriched = enrich_decision_work_brief_markdown(
        brief_markdown=original,
        interpretation_read=load_json_object(LAUNCH_READ_PATH),
        rules_contract=load_json_object(RULES_PATH),
    )

    assert load_markdown(LAUNCH_BRIEF_PATH) == original
    assert enriched.count("## What the interpretation adds") == 1
    assert "## What this does not prove" in enriched
    assert "## Evidence and limits" in enriched
    assert "Checked-in-safe sources are compressed" in enriched
    assert "not as a settled account" in enriched
    assert "This enrichment remains provisional" in enriched


def test_patched_enrichment_section_is_less_repetitive_and_less_template_shaped() -> None:
    for brief_path, read_path in (
        (LAUNCH_BRIEF_PATH, LAUNCH_READ_PATH),
        (DEPLOY_BRIEF_PATH, DEPLOY_READ_PATH),
    ):
        enriched = enrich_decision_work_brief_markdown(
            brief_markdown=load_markdown(brief_path),
            interpretation_read=load_json_object(read_path),
            rules_contract=load_json_object(RULES_PATH),
        )
        section = _main_enrichment_section(enriched)
        sentences = _sentences(section)

        assert len(sentences) == len(set(sentences))
        assert section.count("provisional") <= 1
        assert section.count("The decision is framed as") == 1
        assert section.count("What becomes clearer for action") == 1
        assert section.count("What appears sharpened as a descriptive caution") == 1
        for forbidden in FORBIDDEN_MAIN_BODY_STRINGS:
            assert forbidden not in section


def test_patched_enrichment_keeps_evidence_only_fields_out_of_main_body() -> None:
    section = _main_enrichment_section(GENERATED_DEPLOY_PATH.read_text(encoding="utf-8"))

    for field_name in EVIDENCE_ONLY_FIELD_NAMES:
        assert field_name not in section
    assert "48-hour backlog diagnostic" in section
    assert "The visible thresholds are" in section
    assert "The evidence gates are" in section


def test_patched_checked_in_outputs_preserve_non_claims_and_custody() -> None:
    for path in [GENERATED_LAUNCH_PATH, GENERATED_DEPLOY_PATH]:
        text = path.read_text(encoding="utf-8")
        section = _main_enrichment_section(text)

        assert text.count("## What the interpretation adds") == 1
        assert "Human validation: no" in text
        assert "Product proof: no" in text
        assert "Answer-quality scoring: no" in text
        assert "Agent action authorization: no" in text
        assert "Runtime invoked: no" in text
        assert "Skill invoked: no" in text
        assert "Model calls: 0" in text
        assert "does not prove Lolla improved the decision" in section


def test_pr142_docs_and_outputs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            PATCH_DOC_PATH,
            BUILDER_DOC_PATH,
            PR141_DOC_PATH,
            PR141_REVIEW_PATH,
            GENERATED_LAUNCH_PATH,
            GENERATED_DEPLOY_PATH,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_pr142_touched_files_do_not_include_private_markers() -> None:
    for path in [
        PATCH_DOC_PATH,
        BUILDER_DOC_PATH,
        GENERATED_LAUNCH_PATH,
        GENERATED_DEPLOY_PATH,
        Path(__file__),
    ]:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVACY_MARKERS:
            assert marker not in text
