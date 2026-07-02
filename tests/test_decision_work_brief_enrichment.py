from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.decision_work_brief_enrichment import (
    DecisionWorkBriefEnrichmentInputError,
    enrich_decision_work_brief_markdown,
    load_json_object,
    load_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json"
)
BUILDER_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-offline-enriched-builder-v0.md"
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
EVIDENCE_ONLY_FIELD_NAMES = (
    "live_options",
    "abandoned_or_rejected_options",
    "noisy_friction",
    "lost_value",
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


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _main_enrichment_section(markdown: str) -> str:
    start = markdown.index("## What the interpretation adds")
    end = markdown.index("## What still might be wrong")
    return markdown[start:end]


def test_builder_generates_enriched_markdown_without_mutating_original() -> None:
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
    assert "### Interpretation enrichment limits" in enriched
    assert "This enrichment remains provisional" in enriched
    assert "does not prove Lolla improved the decision" in enriched


def test_builder_excludes_evidence_only_fields_from_main_enrichment_section() -> None:
    enriched = enrich_decision_work_brief_markdown(
        brief_markdown=load_markdown(DEPLOY_BRIEF_PATH),
        interpretation_read=load_json_object(DEPLOY_READ_PATH),
        rules_contract=load_json_object(RULES_PATH),
    )
    main_section = _main_enrichment_section(enriched)

    for field_name in EVIDENCE_ONLY_FIELD_NAMES:
        assert field_name not in main_section
    assert "field_group" not in main_section
    assert "source_status:" not in main_section
    assert "quality score" not in main_section
    assert "What appears sharpened as a descriptive caution" in main_section
    assert "48-hour bottleneck diagnostic" in main_section


def test_cli_generates_launch_and_deploy_enriched_markdown(tmp_path: Path) -> None:
    cases = (
        (LAUNCH_BRIEF_PATH, LAUNCH_READ_PATH, "launch.md", "paid, scoped private-pilot offer"),
        (DEPLOY_BRIEF_PATH, DEPLOY_READ_PATH, "deploy.md", "48-hour backlog diagnostic"),
    )
    for brief_path, read_path, filename, expected in cases:
        output_path = tmp_path / filename
        result = subprocess.run(
            [
                sys.executable,
                "scripts/evals/enrich_decision_work_brief.py",
                "--brief",
                str(brief_path),
                "--interpretation-read",
                str(read_path),
                "--rules",
                str(RULES_PATH),
                "--out",
                str(output_path),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        assert result.returncode == 0, result.stderr
        markdown = output_path.read_text(encoding="utf-8")
        assert markdown.count("## What the interpretation adds") == 1
        assert expected in markdown
        assert "Human validation: no" in markdown
        assert "Product proof: no" in markdown
        assert "Answer-quality scoring: no" in markdown
        assert "Agent action authorization: no" in markdown
        assert "Runtime invoked: no" in markdown
        assert "Skill invoked: no" in markdown
        assert "Model calls: 0" in markdown


def test_cli_rejects_same_input_and_output_path() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/enrich_decision_work_brief.py",
            "--brief",
            str(LAUNCH_BRIEF_PATH),
            "--interpretation-read",
            str(LAUNCH_READ_PATH),
            "--rules",
            str(RULES_PATH),
            "--out",
            str(LAUNCH_BRIEF_PATH),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "output path must be different" in result.stderr
    assert str(REPO_ROOT) not in result.stderr


def test_builder_rejects_bad_rules_schema(tmp_path: Path) -> None:
    bad_rules = _json(RULES_PATH)
    bad_rules["schema_version"] = "unsupported"

    with pytest.raises(DecisionWorkBriefEnrichmentInputError, match="rules schema"):
        enrich_decision_work_brief_markdown(
            brief_markdown=load_markdown(LAUNCH_BRIEF_PATH),
            interpretation_read=load_json_object(LAUNCH_READ_PATH),
            rules_contract=bad_rules,
        )


def test_builder_rejects_nonconservative_interpretation_read() -> None:
    bad_read = _json(LAUNCH_READ_PATH)
    bad_read["custody_flags"]["product_proof"] = True

    with pytest.raises(DecisionWorkBriefEnrichmentInputError, match="custody"):
        enrich_decision_work_brief_markdown(
            brief_markdown=load_markdown(LAUNCH_BRIEF_PATH),
            interpretation_read=bad_read,
            rules_contract=load_json_object(RULES_PATH),
        )


def test_builder_rejects_rules_that_allow_evidence_only_fields() -> None:
    bad_rules = _json(RULES_PATH)
    bad_rules["allowed_user_facing_fields"].append(
        {
            "field_name": "lost_value",
            "source_refs_required": True,
            "source_status_required": True,
            "uncertainty_required": True,
            "interpretation_basis_required": True,
            "privacy_limit_required": True,
            "human_review_required_flag_required": True,
            "must_not_be_used_as_quality_label": True,
        }
    )

    with pytest.raises(DecisionWorkBriefEnrichmentInputError, match="evidence-only"):
        enrich_decision_work_brief_markdown(
            brief_markdown=load_markdown(LAUNCH_BRIEF_PATH),
            interpretation_read=load_json_object(LAUNCH_READ_PATH),
            rules_contract=bad_rules,
        )


def test_checked_in_builder_outputs_exist_and_are_safe() -> None:
    for path in [GENERATED_LAUNCH_PATH, GENERATED_DEPLOY_PATH]:
        assert path.exists()
        markdown = path.read_text(encoding="utf-8")
        assert markdown.count("## What the interpretation adds") == 1
        assert "## What this does not prove" in markdown
        assert "## Evidence and limits" in markdown
        assert "### Interpretation enrichment limits" in markdown
        assert "Product proof: no" in markdown
        assert "Human validation: no" in markdown
        assert "Answer-quality scoring: no" in markdown
        assert "Agent action authorization: no" in markdown
        assert "does not prove Lolla improved the decision" in markdown
        for marker in PRIVACY_MARKERS:
            assert marker not in markdown


def test_builder_docs_and_tests_do_not_include_private_markers() -> None:
    for path in [
        BUILDER_DOC_PATH,
        Path(__file__),
        GENERATED_LAUNCH_PATH,
        GENERATED_DEPLOY_PATH,
    ]:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVACY_MARKERS:
            assert marker not in text
